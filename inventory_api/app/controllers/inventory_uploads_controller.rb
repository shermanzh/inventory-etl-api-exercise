# Belongs in controller as it handles HTTP input/output
# Implements HTTP operations "create" and "index" action

class InventoryUploadsController < ApplicationController
  UPLOAD_FIELDS = %i[
    upc internal_id price quantity department name properties tags
  ].freeze

  # Reads JSON array, rejects empty upload, generates one UUID batch ID, builds an InventoryUnit for every row, validates every row, saves the batch, returns batch ID and record count
  def create
    rows = permitted_rows
    return render_empty_upload if rows.empty?

    batch_id = SecureRandom.uuid # Assigns batch ID to all records that arrived together
    units = rows.map { |attributes| InventoryUnit.new(attributes.merge(batch_id: batch_id)) } # Each JSON unit becomes InventoryUnit.new(..)
    validation_errors = collect_validation_errors(units)

    if validation_errors.any?
      render json: { errors: validation_errors }, status: :unprocessable_content
      return
    end

    units.each(&:save!) # Mongoid writes one MongoDB document per inventory unit if every model is valid
    render json: { batch_id: batch_id, number_of_units: units.length }, status: :created
  end

  # Groups stored records by batch_id, counts records in each batch, calculates average price and total quantity, and returns summaries as JSON
  def index
    summaries = InventoryUnit.collection.aggregate(summary_pipeline).map do |document|
      {
        batch_id: document.fetch("_id"),
        number_of_units: document.fetch("number_of_units"),
        average_price: decimal_number(document.fetch("average_price")).round(2),
        total_quantity: decimal_number(document.fetch("total_quantity"))
      }
    end

    render json: summaries
  end

  private

  # Permits only expected fields, preventing arbitrary unexpected fields from entering MongoDB
  def permitted_rows
    rows = params[:_json]
    unless rows.is_a?(Array) && rows.all? { |row| row.is_a?(ActionController::Parameters) }
      raise ActionController::ParameterMissing, "request body must be a JSON array"
    end

    rows.map do |row|
      row.permit(
        *UPLOAD_FIELDS.excluding(:properties, :tags),
        properties: {},
        tags: []
      ).to_h
    end
  end

  def collect_validation_errors(units)
    units.each_with_index.filter_map do |unit, index|
      next if unit.valid?

      { index: index, errors: unit.errors.to_hash }
    end
  end

  def render_empty_upload
    render json: { errors: [ "request body must contain at least one inventory unit" ] },
      status: :unprocessable_content
  end

  def summary_pipeline
    [
      {
        "$group" => {
          "_id" => "$batch_id",
          "number_of_units" => { "$sum" => 1 },
          "average_price" => { "$avg" => "$price" },
          "total_quantity" => { "$sum" => "$quantity" },
          "created_at" => { "$min" => "$created_at" }
        }
      },
      { "$sort" => { "created_at" => -1 } }
    ]
  end

  def decimal_number(value)
    value = value.to_big_decimal if value.respond_to?(:to_big_decimal)
    value.to_f
  end
end

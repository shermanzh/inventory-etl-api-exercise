# Tests complete HTTP behavior of app/controllers/inventory_uploads_controller.rb
# Tests the following: uploading a batch, sharing one batch ID, recording creation timestamps, rejecting invalid batches or empty uploads, and returning correct summaries
# This is an integration test as it cross several layers: route → controller → model → MongoDB → JSON response

require "test_helper"

class InventoryUploadsTest < ActionDispatch::IntegrationTest
  setup do
    InventoryUnit.delete_all
  end

  test "POST creates one batch containing all uploaded units" do
    post inventory_uploads_path(format: :json), params: valid_payload, as: :json

    assert_response :created
    response_body = response.parsed_body
    assert_equal 2, response_body.fetch("number_of_units")
    assert_match(/\A[0-9a-f-]{36}\z/, response_body.fetch("batch_id"))

    units = InventoryUnit.all.to_a
    assert_equal 2, units.length
    assert_equal [ response_body.fetch("batch_id") ], units.map(&:batch_id).uniq
    assert units.all?(&:created_at)
    assert_equal({ "department" => "TOOLS" }, units.first.properties)
    assert_equal [ "high_margin" ], units.first.tags
  end

  test "POST validates every unit before saving the batch" do
    invalid_payload = valid_payload
    invalid_payload[1] = invalid_payload[1].merge(upc: "invalid", internal_id: "")

    post inventory_uploads_path(format: :json), params: invalid_payload, as: :json

    assert_response :unprocessable_content
    assert_equal 0, InventoryUnit.count
    assert_equal 1, response.parsed_body.fetch("errors").first.fetch("index")
  end

  test "POST rejects an empty batch" do
    post inventory_uploads_path(format: :json), params: [], as: :json

    assert_response :unprocessable_content
    assert_equal 0, InventoryUnit.count
  end

  test "GET summarizes units by batch" do
    post inventory_uploads_path(format: :json), params: valid_payload, as: :json
    first_batch_id = response.parsed_body.fetch("batch_id")
    post inventory_uploads_path(format: :json), params: [ valid_payload.first ], as: :json
    second_batch_id = response.parsed_body.fetch("batch_id")

    get inventory_uploads_path(format: :json)

    assert_response :success
    summaries = response.parsed_body.index_by { |summary| summary.fetch("batch_id") }
    assert_equal 2, summaries.length
    assert_equal 2, summaries.fetch(first_batch_id).fetch("number_of_units")
    assert_equal 15.0, summaries.fetch(first_batch_id).fetch("average_price")
    assert_equal 5.0, summaries.fetch(first_batch_id).fetch("total_quantity")
    assert_equal 1, summaries.fetch(second_batch_id).fetch("number_of_units")
    assert_equal 10.0, summaries.fetch(second_batch_id).fetch("average_price")
    assert_equal 2.0, summaries.fetch(second_batch_id).fetch("total_quantity")
  end

  private

  def valid_payload
    [
      {
        upc: "123456",
        internal_id: "",
        price: 10.0,
        quantity: 2,
        department: "TOOLS",
        name: "Widget Large",
        properties: { department: "TOOLS" },
        tags: [ "high_margin" ]
      },
      {
        upc: "",
        internal_id: "biz_id_record-2",
        price: 20.0,
        quantity: 3,
        department: "TOOLS",
        name: "Widget Small",
        properties: { department: "TOOLS" },
        tags: [ "duplicate_sku", "low_margin" ]
      }
    ]
  end
end

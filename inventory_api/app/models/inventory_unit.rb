class InventoryUnit
  include Mongoid::Document
  include Mongoid::Timestamps::Created

  field :batch_id, type: String
  field :upc, type: String
  field :internal_id, type: String
  field :price, type: BigDecimal
  field :quantity, type: BigDecimal
  field :department, type: String
  field :name, type: String
  field :properties, type: Hash, default: -> { {} }
  field :tags, type: Array, default: -> { [] }

  index({ batch_id: 1 })

  validates :batch_id, presence: true
  validates :price, :quantity, presence: true, numericality: true
  validates :upc, format: { with: /\A[0-9]{6,}\z/ }, allow_blank: true
  validates :internal_id, format: { with: /\Abiz_id_.+\z/ }, allow_blank: true
  validate :identifier_present

  private

  def identifier_present
    return if upc.present? || internal_id.present?

    errors.add(:base, "either upc or internal_id must be present")
  end
end

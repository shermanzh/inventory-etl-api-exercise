require "test_helper"

class InventoryUnitTest < ActiveSupport::TestCase
  test "valid unit has a batch identifier and one item identifier" do
    unit = InventoryUnit.new(
      batch_id: "batch-1",
      upc: "123456",
      price: "10.50",
      quantity: "2",
      properties: { "department" => "TOOLS" },
      tags: [ "high_margin" ]
    )

    assert unit.valid?
  end

  test "unit requires either a valid UPC or an internal identifier" do
    unit = InventoryUnit.new(batch_id: "batch-1", price: 10, quantity: 2)

    assert_not unit.valid?
    assert_includes unit.errors[:base], "either upc or internal_id must be present"
  end

  test "internal identifier must use the biz_id prefix" do
    unit = InventoryUnit.new(
      batch_id: "batch-1",
      internal_id: "record-1",
      price: 10,
      quantity: 2
    )

    assert_not unit.valid?
    assert unit.errors[:internal_id].any?
  end
end

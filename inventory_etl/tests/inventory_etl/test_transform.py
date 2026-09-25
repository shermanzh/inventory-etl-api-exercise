import json
import unittest

from inventory_etl import transform


def source_row(**changes):
    row = {
        "ItemNum": "123456",
        "ItemName": "Widget",
        "Cost": "10",
        "Price": "14",
        "In_Stock": "3",
        "Vendor_Number": "Vendor A",
        "Dept_ID": "TOOLS",
        "ItemName_Extra": "Large",
        "Last_Sold": "2020-06-01 00:00:00.000",
        "RowID": "row-1",
        "ExtendedDescription": "A useful widget",
    }
    row.update(changes)
    return row


class TransformTests(unittest.TestCase):
    def test_high_margin_duplicate_row(self):
        output = transform.transform_row(source_row(), {"123456"})
        self.assertIsNotNone(output)
        self.assertEqual(output["price"], "14.98")
        self.assertEqual(output["name"], "Widget Large")
        self.assertEqual(json.loads(output["tags"]), ["duplicate_sku", "high_margin"])
        self.assertEqual(json.loads(output["properties"])["description"], "A useful widget")

    def test_invalid_upc_uses_internal_id(self):
        output = transform.transform_row(
            source_row(ItemNum="BAD-ID", RowID="abc", Cost="0", Price="5"), set()
        )
        self.assertEqual(output["upc"], "")
        self.assertEqual(output["internal_id"], "biz_id_abc")
        self.assertEqual(output["price"], "5.35")

    def test_exactly_thirty_percent_uses_nine_percent_and_no_margin_tag(self):
        output = transform.transform_row(source_row(Price="13"), set())
        self.assertEqual(output["price"], "14.17")
        self.assertEqual(json.loads(output["tags"]), [])

    def test_non_2020_row_is_filtered(self):
        output = transform.transform_row(source_row(Last_Sold="2019-12-31"), set())
        self.assertIsNone(output)


if __name__ == "__main__":
    unittest.main()


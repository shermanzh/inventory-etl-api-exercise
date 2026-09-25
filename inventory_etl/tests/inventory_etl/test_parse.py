import io
import unittest

from inventory_etl import parse


HEADERS = [
    "ItemNum",
    "ItemName",
    "Cost",
    "Price",
    "In_Stock",
    "Vendor_Number",
    "Dept_ID",
    "ItemName_Extra",
    "Last_Sold",
    "RowID",
    "ItemNum",
]


class ParseTests(unittest.TestCase):
    def test_dict_reader_keeps_first_duplicate_header(self):
        text = "\n".join(
            [
                "|".join(HEADERS),
                "123456|Widget|10|14|3|Vendor|TOOLS|Large|2020-06-01|row-1|joined",
            ]
        )
        rows = parse.parse_stream(io.StringIO(text))
        self.assertEqual(rows[0]["ItemNum"], "123456")
        self.assertEqual(rows[0]["ItemNum__2"], "joined")

    def test_separator_and_blank_rows_are_ignored(self):
        text = "\n".join(
            [
                "|".join(HEADERS),
                "|".join("-" * len(name) for name in HEADERS),
                "||||||||||",
                "123456|Widget|10|14|3|Vendor|TOOLS||2020-06-01|row-1|joined",
            ]
        )
        self.assertEqual(len(parse.parse_bytes(text.encode("utf-8"))), 1)

    def test_missing_required_column_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing columns"):
            parse.parse_stream(io.StringIO("ItemNum|Price\n123456|10"))


if __name__ == "__main__":
    unittest.main()


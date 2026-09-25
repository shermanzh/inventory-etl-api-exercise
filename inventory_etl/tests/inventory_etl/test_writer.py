import csv
import tempfile
import unittest
from pathlib import Path

from inventory_etl.writer import write_csv


class WriterTests(unittest.TestCase):
    def test_writes_header_and_rows(self):
        row = {
            "upc": "123456",
            "internal_id": "",
            "price": "10.70",
            "quantity": "2",
            "department": "TOOLS",
            "name": "Widget",
            "properties": '{"department":"TOOLS"}',
            "tags": '["high_margin"]',
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "export.csv"
            write_csv([row], output)
            with output.open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(rows, [row])


if __name__ == "__main__":
    unittest.main()


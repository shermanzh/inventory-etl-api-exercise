import unittest

from inventory_etl.duplicates import find_duplicate_item_numbers


class DuplicateTests(unittest.TestCase):
    def test_pre_scan_returns_only_duplicate_item_numbers(self):
        rows = [
            {"ItemNum": "A"},
            {"ItemNum": "B"},
            {"ItemNum": "A"},
            {"ItemNum": ""},
        ]
        self.assertEqual(find_duplicate_item_numbers(rows), {"A"})


if __name__ == "__main__":
    unittest.main()


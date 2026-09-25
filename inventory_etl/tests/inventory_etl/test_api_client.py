import json
import unittest
from unittest.mock import patch

from inventory_etl import api_client


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


class ApiClientTests(unittest.TestCase):
    @patch("inventory_etl.api_client.urlopen")
    def test_upload_posts_json_array(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(b'{"batch_id":"batch-1"}')
        result = api_client.upload_inventory(
            "http://localhost:3000/",
            [
                {
                    "upc": "123456",
                    "price": "10.70",
                    "quantity": "2.0000",
                    "properties": '{"department":"TOOLS"}',
                    "tags": '["high_margin"]',
                }
            ],
        )

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "http://localhost:3000/inventory_uploads.json")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(
            json.loads(request.data),
            [
                {
                    "upc": "123456",
                    "price": 10.7,
                    "quantity": 2.0,
                    "properties": {"department": "TOOLS"},
                    "tags": ["high_margin"],
                }
            ],
        )
        self.assertEqual(result, {"batch_id": "batch-1"})

    def test_upload_row_rejects_invalid_structured_fields(self):
        with self.assertRaisesRegex(ValueError, "Invalid JSON in tags"):
            api_client.row_for_api(
                {
                    "price": "10",
                    "quantity": "2",
                    "properties": "{}",
                    "tags": "not-json",
                }
            )

    @patch("inventory_etl.api_client.urlopen")
    def test_list_uploads_gets_json(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(b'[{"batch_id":"batch-1"}]')
        result = api_client.list_uploads("http://localhost:3000")

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        self.assertEqual(result, [{"batch_id": "batch-1"}])


if __name__ == "__main__":
    unittest.main()

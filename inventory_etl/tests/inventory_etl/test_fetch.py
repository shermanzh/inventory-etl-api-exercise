import unittest
from unittest.mock import patch

from inventory_etl import fetch


HTML = """
<div id="bucket-value">example-bucket</div>
<div id="region-value" data-region="us-west-2">Oregon</div>
<div id="object-value">
  <span class="path">folder</span><span class="path">inventory file.csv</span>
</div>
"""


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.body


class FetchTests(unittest.TestCase):
    def test_parse_s3_location_and_url(self):
        location = fetch.parse_s3_location(HTML)
        self.assertEqual(location.bucket, "example-bucket")
        self.assertEqual(location.region, "us-west-2")
        self.assertEqual(location.object_key, "folder/inventory file.csv")
        self.assertEqual(
            location.url,
            "https://example-bucket.s3.us-west-2.amazonaws.com/"
            "folder/inventory%20file.csv",
        )

    def test_bitbucket_source_url_becomes_raw_url(self):
        url = "https://bitbucket.org/team/repo/src/main/path/file.html"
        self.assertEqual(
            fetch.bitbucket_raw_url(url),
            "https://bitbucket.org/team/repo/raw/main/path/file.html",
        )

    @patch("inventory_etl.fetch.urlopen")
    def test_get_bytes_uses_get_request(self, mock_urlopen):
        mock_urlopen.return_value = FakeResponse(b"payload")
        self.assertEqual(fetch.get_bytes("https://example.test/file"), b"payload")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, "https://example.test/file")
        self.assertEqual(request.get_method(), "GET")


if __name__ == "__main__":
    unittest.main()


"""Discover and download the public S3 inventory object."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from . import config


@dataclass(frozen=True)
class S3Location:
    bucket: str
    region: str
    object_key: str

    @property
    def url(self) -> str:
        encoded_key = quote(self.object_key.lstrip("/"), safe="/")
        return config.S3_URL_TEMPLATE.format(
            bucket=self.bucket,
            region=self.region,
            object_key=encoded_key,
        )

# Looks for bucket, region, and object key in the HTML of the Bitbucket page
# Produces a S3Location object with the bucket, region, and object key
class _S3LocationHTMLParser(HTMLParser):
    wanted_ids = {"bucket-value", "region-value", "object-value"}

    def __init__(self) -> None:
        super().__init__()
        self.values: dict[str, list[str]] = {
            element_id: [] for element_id in self.wanted_ids
        }
        self.region_code = ""
        self._active_id: str | None = None
        self._div_depth = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        if tag != "div":
            return

        attributes = dict(attrs)
        if self._active_id is not None:
            self._div_depth += 1
            return

        element_id = attributes.get("id")
        if element_id in self.wanted_ids:
            self._active_id = element_id
            self._div_depth = 1
            if element_id == "region-value":
                self.region_code = (attributes.get("data-region") or "").strip()

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._active_id is not None:
            self._div_depth -= 1
            if self._div_depth == 0:
                self._active_id = None

    def handle_data(self, data: str) -> None:
        if self._active_id is None:
            return
        value = data.strip()
        if value:
            self.values[self._active_id].append(value)


def parse_s3_location(html: str) -> S3Location:
    parser = _S3LocationHTMLParser()
    parser.feed(html)

    bucket = "".join(parser.values["bucket-value"]).strip()
    region = parser.region_code
    object_parts = [
        part.strip().strip("/")
        for part in parser.values["object-value"]
        if part.strip().strip("/")
    ]
    object_key = "/".join(object_parts)

    if not bucket or not region or not object_key:
        raise ValueError("Could not find the S3 bucket, region, and object path in the HTML")
    return S3Location(bucket=bucket, region=region, object_key=object_key)


def bitbucket_raw_url(url: str) -> str:
    """Convert a Bitbucket source-page URL to its raw-file URL."""

    parsed = urlsplit(url)
    if parsed.netloc != "bitbucket.org":
        return url

    path_parts = parsed.path.split("/")
    try:
        source_index = path_parts.index("src")
    except ValueError:
        return url
    path_parts[source_index] = "raw"
    return urlunsplit((parsed.scheme, parsed.netloc, "/".join(path_parts), "", ""))


def get_bytes(url: str, timeout: float = config.HTTP_TIMEOUT_SECONDS) -> bytes:
    request = Request(url, headers={"User-Agent": config.USER_AGENT})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except HTTPError as error:
        raise RuntimeError(f"GET {url} failed with HTTP {error.code}") from error
    except URLError as error:
        raise RuntimeError(f"GET {url} failed: {error.reason}") from error

# Converts Bitbucket display URL into a raw URL and makes an HTTP GET request, returns HTML text
def discover_s3_location(initial_html_url: str = config.INITIAL_HTML_URL) -> S3Location:
    html_url = bitbucket_raw_url(initial_html_url)
    html = get_bytes(html_url).decode("utf-8")
    return parse_s3_location(html)

# Performs second GET request to download the S3 object and returns the S3Location and the bytes of the object
# Returns location as the parsed S3Location, and content as the raw CSV file as bytes
def fetch_inventory_bytes(
    initial_html_url: str = config.INITIAL_HTML_URL,
) -> tuple[S3Location, bytes]:
    location = discover_s3_location(initial_html_url)
    return location, get_bytes(location.url)

# Saves raw CSV file to a file location
def save_bytes(content: bytes, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)


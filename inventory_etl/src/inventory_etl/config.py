"""Configuration constants for the inventory ETL."""

from decimal import Decimal
from pathlib import Path


INITIAL_HTML_URL = (
    "https://bitbucket.org/cityhive/jobs/src/master/"
    "integration-eng/integration-entryfile.html"
)
S3_URL_TEMPLATE = "https://{bucket}.s3.{region}.amazonaws.com/{object_key}"

DEFAULT_API_BASE_URL = "http://localhost:3000"
INVENTORY_UPLOADS_PATH = "/inventory_uploads.json"
HTTP_TIMEOUT_SECONDS = 30.0
USER_AGENT = "inventory-etl/1.0"

DEFAULT_DOWNLOAD_PATH = Path("downloaded_inventory.csv")
DEFAULT_OUTPUT_PATH = Path("inventory_export.csv")

MARGIN_THRESHOLD = Decimal("0.30")
HIGH_MARGIN_PRICE_MULTIPLIER = Decimal("1.07")
OTHER_PRICE_MULTIPLIER = Decimal("1.09")

OUTPUT_FIELDS = (
    "upc",
    "internal_id",
    "price",
    "quantity",
    "department",
    "name",
    "properties",
    "tags",
)

REQUIRED_INPUT_FIELDS = frozenset(
    {
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
    }
)


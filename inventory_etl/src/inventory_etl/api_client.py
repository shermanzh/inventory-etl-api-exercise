"""Small JSON client for the Rails inventory uploads API."""

from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from . import config


def inventory_uploads_url(api_base_url: str) -> str:
    return f"{api_base_url.rstrip('/')}{config.INVENTORY_UPLOADS_PATH}"


def request_json(
    method: str,
    url: str,
    payload: Any = None,
    timeout: float = config.HTTP_TIMEOUT_SECONDS,
) -> Any:
    data = None
    headers = {
        "Accept": "application/json",
        "User-Agent": config.USER_AGENT,
    }
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        message = f"{method} {url} failed with HTTP {error.code}"
        raise RuntimeError(f"{message}: {detail}" if detail else message) from error
    except URLError as error:
        raise RuntimeError(f"{method} {url} failed: {error.reason}") from error

    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{method} {url} returned invalid JSON") from error


def upload_inventory(
    api_base_url: str, rows: Iterable[Mapping[str, str]]
) -> Any:
    return request_json(
        "POST",
        inventory_uploads_url(api_base_url),
        payload=[row_for_api(row) for row in rows],
    )


def list_uploads(api_base_url: str) -> Any:
    return request_json("GET", inventory_uploads_url(api_base_url))


def row_for_api(row: Mapping[str, str]) -> dict[str, Any]:
    """Convert a CSV-ready transformed row into a typed JSON record."""

    result: dict[str, Any] = dict(row)
    for field in ("price", "quantity"):
        try:
            result[field] = float(Decimal(str(result[field])))
        except (InvalidOperation, KeyError) as error:
            raise ValueError(f"Invalid numeric {field}: {result.get(field)!r}") from error

    result["properties"] = structured_value(result, "properties", dict)
    result["tags"] = structured_value(result, "tags", list)
    return result


def structured_value(
    row: Mapping[str, Any], field: str, expected_type: type
) -> Any:
    value = row.get(field)
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in {field}: {value!r}") from error
    if not isinstance(value, expected_type):
        raise ValueError(f"{field} must contain a JSON {expected_type.__name__}")
    return value

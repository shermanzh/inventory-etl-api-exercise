"""Apply per-row inventory business rules."""

from __future__ import annotations

import json
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Iterable, Mapping

from . import config


UPC_PATTERN = re.compile(r"[0-9]{6,}\Z")


def clean(value: str | None) -> str:
    result = (value or "").strip()
    return "" if result.casefold() in {"", "null"} else result


def decimal_value(value: str | None, column: str) -> Decimal:
    cleaned = clean(value)
    try:
        return Decimal(cleaned or "0")
    except InvalidOperation as error:
        raise ValueError(f"Invalid decimal in {column}: {value!r}") from error


def sold_during_2020(value: str | None) -> bool:
    date_text = clean(value)
    if not date_text:
        return False
    try:
        return datetime.fromisoformat(date_text).year == 2020
    except ValueError:
        return False


def margin_ratio(price: Decimal, cost: Decimal) -> Decimal:
    if cost == 0:
        if price > 0:
            return Decimal("Infinity")
        if price < 0:
            return Decimal("-Infinity")
        return Decimal("0")
    return (price - cost) / cost

# Business rules, clean whitespace
def transform_row(
    row: Mapping[str, str], duplicate_item_numbers: set[str]
) -> dict[str, str] | None:
    if not sold_during_2020(row.get("Last_Sold")):
        return None # Disincludes items not sold in 2020

    item_number = clean(row.get("ItemNum"))
    item_name = clean(row.get("ItemName"))
    item_extra = clean(row.get("ItemName_Extra"))
    department = clean(row.get("Dept_ID"))
    vendor = clean(row.get("Vendor_Number"))
    description = clean(row.get("ExtendedDescription")) or item_name
    price = decimal_value(row.get("Price"), "Price")
    cost = decimal_value(row.get("Cost"), "Cost")
    margin = margin_ratio(price, cost)
    high_margin = margin > config.MARGIN_THRESHOLD

    multiplier = ( # If (price - cost) / cost > 30%, it is high-margin and * 1.07, otherwise * 1.09 and round to 2 decimal places
        config.HIGH_MARGIN_PRICE_MULTIPLIER
        if high_margin
        else config.OTHER_PRICE_MULTIPLIER
    )
    adjusted_price = (price * multiplier).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP # Decimal instead of float so monetary rounding is predictable
    )

    # Tags field for duplicate SKU, high or low margins and encoded as JSON for CSV storage
    tags: list[str] = []
    if item_number in duplicate_item_numbers:
        tags.append("duplicate_sku")
    if margin > config.MARGIN_THRESHOLD:
        tags.append("high_margin")
    elif margin < config.MARGIN_THRESHOLD:
        tags.append("low_margin")

    # Validates UPC as ASCII digits only and at least 6 characters long, otherwise use internal_id
    valid_upc = bool(UPC_PATTERN.fullmatch(item_number))
    return {
        "upc": item_number if valid_upc else "",
        "internal_id": "" if valid_upc else f"biz_id_{clean(row.get('RowID'))}",
        "price": f"{adjusted_price:.2f}",
        "quantity": clean(row.get("In_Stock")),
        "department": department,
        "name": " ".join(part for part in (item_name, item_extra) if part), # Join ItemName and ItemName_Extra with a space
        "properties": json.dumps( # Contains a JSON string
            {
                "department": department,
                "vendor": vendor,
                "description": description,
            },
            separators=(",", ":"),
            ensure_ascii=False,
        ),
        "tags": json.dumps(tags, separators=(",", ":")), # Contains a JSON string
    }


def transform_rows(
    rows: Iterable[Mapping[str, str]], duplicate_item_numbers: set[str]
) -> list[dict[str, str]]:
    transformed: list[dict[str, str]] = []
    for row in rows:
        output_row = transform_row(row, duplicate_item_numbers)
        if output_row is not None:
            transformed.append(output_row)
    return transformed


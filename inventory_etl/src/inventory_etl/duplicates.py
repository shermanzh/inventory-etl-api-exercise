"""Pre-scan inventory rows for duplicate ItemNum values."""

from collections import Counter
from typing import Iterable, Mapping


def find_duplicate_item_numbers(rows: Iterable[Mapping[str, str]]) -> set[str]:
    counts = Counter(
        (row.get("ItemNum") or "").strip()
        for row in rows
        if (row.get("ItemNum") or "").strip()
    )
    return {item_number for item_number, count in counts.items() if count > 1}


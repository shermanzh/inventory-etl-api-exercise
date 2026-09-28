"""Parse the pipe-delimited inventory with csv.DictReader."""

from __future__ import annotations

import csv
import io
from collections import Counter
from pathlib import Path
from typing import Iterable, TextIO

from .config import REQUIRED_INPUT_FIELDS


def unique_fieldnames(fieldnames: Iterable[str]) -> list[str]:
    """Suffix repeated headers so DictReader does not overwrite earlier values."""

    counts: Counter[str] = Counter()
    unique_names: list[str] = []
    for raw_name in fieldnames:
        name = raw_name.strip()
        counts[name] += 1
        occurrence = counts[name]
        unique_names.append(name if occurrence == 1 else f"{name}__{occurrence}")
    return unique_names

# Creates DictReader with unique fieldnames, checks for required fields, and filters out rows with empty or invalid ItemNum
def parse_stream(stream: TextIO) -> list[dict[str, str]]:
    reader = csv.DictReader(stream, delimiter="|")
    original_fieldnames = reader.fieldnames
    if not original_fieldnames:
        raise ValueError("The input file does not have a header row")
    reader.fieldnames = unique_fieldnames(original_fieldnames)

    missing = REQUIRED_INPUT_FIELDS.difference(reader.fieldnames)
    if missing:
        raise ValueError(f"The input file is missing columns: {', '.join(sorted(missing))}")

    rows: list[dict[str, str]] = []
    for row in reader:
        item_number = (row.get("ItemNum") or "").strip()
        if not item_number or set(item_number) == {"-"}:
            continue
        rows.append(row)
    return rows


def parse_bytes(content: bytes) -> list[dict[str, str]]:
    stream = io.StringIO(content.decode("utf-8-sig"), newline="")
    return parse_stream(stream)


def parse_file(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return parse_stream(stream)


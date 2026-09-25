"""Write transformed inventory records to CSV."""

import csv
from pathlib import Path
from typing import Iterable, Mapping

from .config import OUTPUT_FIELDS


def write_csv(rows: Iterable[Mapping[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


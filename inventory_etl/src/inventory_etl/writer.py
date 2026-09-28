"""Write transformed inventory records to CSV."""
# generate_csv command calls here

import csv
from pathlib import Path
from typing import Iterable, Mapping

from .config import OUTPUT_FIELDS

# Creates destination file, writes output header, and writes every transformed record
# Note: Through generate_csv, the outputted CSV is the final deliverable, and is not automatically used by upload command
def write_csv(rows: Iterable[Mapping[str, str]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


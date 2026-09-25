# Inventory ETL

A standard-library-only Python implementation of the inventory extraction and
transformation exercise. It discovers the S3 object from the supplied Bitbucket
HTML, downloads and parses the pipe-delimited source, transforms inventory sold
during 2020, and either writes CSV or uploads JSON to the Rails API.

## Commands

Generate CSV directly from the downloaded bytes:

```bash
python3 integration-exercise.py generate_csv \
  --flow memory \
  --output inventory_export.csv
```

Save the S3 object locally before parsing:

```bash
python3 integration-exercise.py generate_csv \
  --flow file \
  --download-path downloaded_inventory.csv \
  --output inventory_export.csv
```

Upload transformed rows to Rails:

```bash
python3 integration-exercise.py upload --api-base-url http://localhost:3000
```

List upload summaries:

```bash
python3 integration-exercise.py list_uploads --api-base-url http://localhost:3000
```

Run the tests without installing anything:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests/inventory_etl -v
```

## Business-rule decisions

- Margin is `(price - cost) / cost`. A positive-price item with zero cost is
  treated as high-margin.
- Exactly 30% margin receives the 9% increase and neither margin tag because the
  tag requirements use strict “more than” and “less than” comparisons.
- Quantity comes from `In_Stock`; department comes from `Dept_ID`.
- The properties description uses `ExtendedDescription` and falls back to
  `ItemName`.
- `properties` is encoded as a JSON object and `tags` as a JSON array within the
  CSV cells.
- Duplicate ItemNum values are pre-scanned across the complete input before the
  2020 filter.
- Repeated source header names are suffixed before `DictReader` emits rows, so
  later joined columns cannot overwrite the primary product fields.


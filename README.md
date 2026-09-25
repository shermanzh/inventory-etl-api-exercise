# Inventory ETL and Storage API

This project implements an inventory extraction, transformation, storage, and reporting workflow.

The Python application discovers and downloads inventory data from Amazon S3, parses and transforms the records, and either generates a CSV or uploads the transformed inventory to a Rails API.

The Rails API validates and stores each inventory unit in MongoDB using Mongoid. Records uploaded together share a batch identifier. The API can return summary statistics for every batch.

## Architecture

```text
Source HTML
    → Amazon S3 inventory
    → Python ETL
    → CSV or JSON upload
    → Rails API
    → MongoDB
    → Batch summaries
```

## Project Structure

```text
inventory_etl/    Python extraction and transformation application
inventory_api/    Rails and Mongoid storage API
```

## Prerequisites

- Python 3.10 or newer
- Ruby 3.4
- Rails 8.1
- MongoDB Community Edition 8.0

The Python application uses only Python standard-library packages.

## Start MongoDB

```bash
brew services start mongodb-community@8.0
```

Verify the connection:

```bash
mongosh --eval 'db.runCommand({ ping: 1 })'
```

## Rails API Setup

```bash
cd inventory_api
bundle install
bin/rails db:create_indexes
bin/rails server
```

The API runs at `http://127.0.0.1:3000`.

Available endpoints:

```text
POST /inventory_uploads.json
GET  /inventory_uploads.json
```

## Python ETL Commands

Open another terminal:

```bash
cd inventory_etl
```

Generate a transformed CSV:

```bash
python3 integration-exercise.py generate_csv \
  --output inventory_export.csv
```

Upload transformed records to Rails:

```bash
python3 integration-exercise.py upload \
  --api-base-url http://127.0.0.1:3000
```

List stored batch summaries:

```bash
python3 integration-exercise.py list_uploads \
  --api-base-url http://127.0.0.1:3000
```

The ETL supports two input flows:

```text
--flow memory    Parse downloaded bytes directly
--flow file      Save the raw download before parsing it
```

## Run the Tests

Python:

```bash
cd inventory_etl

PYTHONPATH=src python3 -m unittest discover \
  -s tests/inventory_etl \
  -v
```

Rails:

```bash
cd inventory_api

bin/rails test
bin/rubocop --cache false
bundle exec brakeman --quiet --no-pager
```

## Current Expected Results

Using the provided source data:

```text
Transformed inventory records: 491
Average transformed price:     19.69
Total quantity:                4250.0
Invalid UPC/internal IDs:      2
High-margin tags:              381
Low-margin tags:               110
Duplicate-SKU tags:            6
```

## Important Implementation Details

- The CSV is parsed with `csv.DictReader`.
- Repeated source headers are disambiguated before parsing.
- Duplicate SKUs are detected across the complete input.
- Prices are calculated with Python `Decimal`.
- Only items sold during 2020 are exported.
- UPC values must contain at least six ASCII digits.
- Invalid UPC records receive a `biz_id_` internal identifier.
- Rails uses Mongoid instead of Active Record.
- Prices and quantities are stored as MongoDB Decimal128 values.
- Every upload receives one shared UUID batch identifier.
- All records are validated before a batch is saved.

## Suggested Review Order

1. `inventory_etl/integration-exercise.py`
2. `inventory_etl/src/inventory_etl/fetch.py`
3. `inventory_etl/src/inventory_etl/parse.py`
4. `inventory_etl/src/inventory_etl/transform.py`
5. `inventory_etl/src/inventory_etl/api_client.py`
6. `inventory_api/config/routes.rb`
7. `inventory_api/app/controllers/inventory_uploads_controller.rb`
8. `inventory_api/app/models/inventory_unit.rb`
9. The Python and Rails test suites

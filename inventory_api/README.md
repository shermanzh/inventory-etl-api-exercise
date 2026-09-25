# Inventory API

Rails API for storing transformed inventory batches in MongoDB with Mongoid.

## Setup

Start the local MongoDB service, install gems, and create the MongoDB index:

```bash
brew services start mongodb-community@8.0
bundle install
bin/rails db:create_indexes
```

Start the API:

```bash
bin/rails server
```

The service listens at `http://127.0.0.1:3000` in development.

## Endpoints

`POST /inventory_uploads.json` accepts a non-empty JSON array of transformed
inventory units. It validates every row before saving and assigns one UUID batch
identifier to the complete upload.

`GET /inventory_uploads.json` returns one summary per batch with `batch_id`,
`number_of_units`, `average_price`, and `total_quantity`.

Run the test suite with:

```bash
bin/rails test
```

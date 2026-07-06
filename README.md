# Orders REST API Service

[![codecov](https://codecov.io/gh/CSCI-GA-2820-SU26-001/orders/graph/badge.svg?token=RA3FAVPWRU)](https://codecov.io/gh/CSCI-GA-2820-SU26-001/orders)
[![CI Build](https://github.com/CSCI-GA-2820-SU26-001/orders/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU26-001/orders/actions/workflows/ci.yml)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


The Orders service is a Flask REST API for managing customer orders and the items inside each order. It stores data in PostgreSQL through SQLAlchemy and includes test coverage for the order model, item model, service routes, and Flask CLI commands.

## Features

- Create, read, update, delete, and list orders
- Add, read, update, delete, and list items in an order
- Validate required order and item fields
- Return JSON error responses for invalid requests
- Run unit tests with a 95% minimum coverage gate

## Technology

- Python 3.12
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Pipenv
- Pytest, pytest-cov, flake8, pylint

## Project Structure

```text
service/
├── __init__.py
├── config.py
├── routes.py
├── common/
│   ├── cli_commands.py
│   ├── error_handlers.py
│   ├── log_handlers.py
│   └── status.py
└── models/
    ├── __init__.py
    ├── order.py
    ├── order_items.py
    └── persistent_base.py

tests/
├── factories.py
├── test_cli_commands.py
├── test_models.py
└── test_routes.py
```

## Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/CSCI-GA-2820-SU26-001/orders.git
cd orders
pipenv install --dev
```

Create a local `.env` file:

```bash
cp dot-env-example .env
```

Edit `.env` so that it contains these local development settings:

```bash
FLASK_APP=wsgi:app
PORT=8080
DATABASE_URI=postgresql+psycopg://postgres:postgres@localhost:5432/postgres
```

Start PostgreSQL if you do not already have a local database running:

```bash
docker run --name orders-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d postgres:15-alpine
```

If the container already exists, start it instead:

```bash
docker start orders-postgres
```

Create the database tables:

```bash
pipenv run flask db-create
```

## Running the Service

Start the service locally:

```bash
pipenv run honcho start
```

The API will be available at:

```text
http://localhost:8080
```

Check the root endpoint:

```bash
curl http://localhost:8080/
```

## Running Tests

Run the full test suite with coverage:

```bash
pipenv run pytest --pspec --cov=service --cov-fail-under=95 --disable-warnings
```

Run lint checks:

```bash
pipenv run flake8 service tests --count --max-complexity=10 --max-line-length=127 --statistics
pipenv run pylint service tests --max-line-length=127
```

The Makefile also provides shortcuts:

```bash
make test
make lint
make run
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Return service information |
| `POST` | `/orders` | Create an order |
| `GET` | `/orders` | List all orders |
| `GET` | `/orders/{order_id}` | Read one order |
| `PUT` | `/orders/{order_id}` | Update one order |
| `DELETE` | `/orders/{order_id}` | Delete one order |
| `POST` | `/orders/{order_id}/items` | Add an item to an order |
| `GET` | `/orders/{order_id}/items` | List all items in an order |
| `GET` | `/orders/{order_id}/items/{item_id}` | Read one item in an order |
| `PUT` | `/orders/{order_id}/items/{item_id}` | Update one item in an order |
| `DELETE` | `/orders/{order_id}/items/{item_id}` | Delete one item from an order |
| `GET` | `/health` | Health check, returns {"status": "OK"} |
| `PUT` | `/orders/{order_id}/cancel` | Cancel an order (action) |

### Query Parameters for Listing Orders

The `GET /orders` endpoint supports filtering with query strings:

| Parameter | Example | Description |
| --- | --- | --- |
| `customer_id` | `/orders?customer_id=1` | Return orders for one customer |
| `status` | `/orders?status=open` | Return orders with a given status |
| `id` | `/orders?id=5` | Return the order with a given id |
| `item_id` | `/orders?item_id=3` | Return orders containing a given item |

Invalid (non-integer) values for `customer_id`, `id`, or `item_id` return `400 Bad Request`.


## Example Requests

Set the base URL:

```bash
BASE_URL=http://localhost:8080
```

Create an order:

```bash
curl -i -X POST "$BASE_URL/orders" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "status": "open"}'
```

List all orders:

```bash
curl -i "$BASE_URL/orders"
```

Read one order:

```bash
curl -i "$BASE_URL/orders/1"
```

Update an order:

```bash
curl -i -X PUT "$BASE_URL/orders/1" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "status": "closed"}'
```

Add an item to an order:

```bash
curl -i -X POST "$BASE_URL/orders/1/items" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 100, "quantity": 2, "price": 19.99}'
```

List all items in an order:

```bash
curl -i "$BASE_URL/orders/1/items"
```

Read one item in an order:

```bash
curl -i "$BASE_URL/orders/1/items/1"
```

Update an item in an order:

```bash
curl -i -X PUT "$BASE_URL/orders/1/items/1" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 200, "quantity": 5, "price": 9.99}'
```

Delete an item from an order:

```bash
curl -i -X DELETE "$BASE_URL/orders/1/items/1"
```

Cancel an order:

```bash
curl -i -X PUT "$BASE_URL/orders/1/cancel"
```

Check service health:

```bash
curl -i "$BASE_URL/health"
```

Delete an order:

```bash
curl -i -X DELETE "$BASE_URL/orders/1"
```

## Data Validation

Order requests require:

- `customer_id`
- optional `status`, which defaults to `open`

Order item requests require:

- `product_id`
- `quantity`, which must be greater than `0`
- `price`, which cannot be negative

Invalid JSON request bodies or missing required fields return `400 Bad Request`. Requests with the wrong or missing `Content-Type` return `415 Unsupported Media Type`.

Cancelling an already cancelled order returns `409 Conflict`.

## License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.

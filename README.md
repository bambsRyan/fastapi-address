# Address Book API

A minimal REST API for managing addresses with geolocation search, built with FastAPI, SQLModel, and Docker.

## Requirements

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

## Quick Start

### With Docker (recommended)

```bash
git clone https://github.com/bambsRyan/fastapi-address.git
cd fastapi-address
cp .env.example .env
docker compose up --build
```

Open the interactive API docs: **http://localhost:8000/docs**

### Without Docker

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/bambsRyan/fastapi-address.git
cd fastapi-address
cp .env.example .env
uv sync
uvicorn app.main:app --reload
```

Open the interactive API docs: **http://localhost:8000/docs**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/addresses/` | Create an address |
| `GET` | `/api/v1/addresses/` | List, search, sort, and paginate addresses |
| `PATCH` | `/api/v1/addresses/{id}` | Partially update an address |
| `DELETE` | `/api/v1/addresses/{id}` | Delete an address |

### Query Parameters — `GET /api/v1/addresses/`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | — | Partial, case-insensitive match |
| `street` | string | — | Partial, case-insensitive match |
| `city` | string | — | Partial, case-insensitive match |
| `country` | string | — | Partial, case-insensitive match |
| `latitude` | float | — | Center latitude for proximity search |
| `longitude` | float | — | Center longitude for proximity search |
| `radius_km` | float | — | Search radius in kilometres (requires `latitude` + `longitude`) |
| `sort_by` | string | `id` | `id` \| `name` \| `street` \| `city` \| `country` |
| `sort_order` | string | `asc` | `asc` \| `desc` |
| `skip` | int | `0` | Records to skip |
| `limit` | int | `10` | Records to return (max 100) |

### Example Requests

**Create an address:**
```bash
curl -X POST http://localhost:8000/api/v1/addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home",
    "street": "123 Main St",
    "city": "Manila",
    "country": "Philippines",
    "latitude": 14.5995,
    "longitude": 120.9842
  }'
```

**Find addresses within 5 km of a point:**
```bash
curl "http://localhost:8000/api/v1/addresses/?latitude=14.5995&longitude=120.9842&radius_km=5"
```

**Paginated and sorted list:**
```bash
curl "http://localhost:8000/api/v1/addresses/?sort_by=name&sort_order=asc&skip=0&limit=10"
```

**Partial update (only city changes):**
```bash
curl -X PATCH http://localhost:8000/api/v1/addresses/1 \
  -H "Content-Type: application/json" \
  -d '{"city": "Quezon City"}'
```

### Response — `GET /api/v1/addresses/`

```json
{
  "total": 42,
  "skip": 0,
  "limit": 10,
  "data": [
    {
      "id": 1,
      "name": "Home",
      "street": "123 Main St",
      "city": "Manila",
      "country": "Philippines",
      "latitude": 14.5995,
      "longitude": 120.9842
    }
  ]
}
```

---

## Running Tests

```bash
uv run pytest
```

---

## Project Structure

```
app/
├── api/v1/endpoints/   # Route handlers
├── core/               # Configuration
├── models/             # SQLModel schemas (Base, Create, Read, Update, Page)
├── services/           # Business logic and database operations
├── database.py         # Engine and session dependency
└── main.py             # App entry point, middleware, error handlers
tests/
├── conftest.py                 # Shared fixtures (engine, db session, HTTP client)
├── test_addresses.py           # HTTP endpoint tests
└── test_address_service.py     # Service layer tests
```

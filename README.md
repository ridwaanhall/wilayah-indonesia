# Wilayah Indonesia API

FastAPI service for Indonesian administrative regions with consistent envelope responses, typed OpenAPI contracts, and full 4-level hierarchy support.

## What You Get

- Full hierarchy: province, regency/city, district, village
- Consistent response envelope on success and error
- Typed OpenAPI payloads for single-region and list endpoints
- Dynamic metadata version from config (`app_version -> api_version`)
- Dynamic error docs URL based on current request base URL
- Landing page at `/` with links to `/api`, `/docs`, and `/openapi.json`

## Endpoints

- `GET /` landing page
- `GET /api/` API index
- `GET /api/health`
- `GET /api/0`
- `GET /api/{kode_provinsi}`
- `GET /api/{kode_provinsi}/{kode_kabupaten}`
- `GET /api/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}`
- `GET /api/kode/{kode}`
- `GET /api/s/{kode_provinsi}`
- `GET /api/s/{kode_provinsi}/{nomor_kabupaten}`
- `GET /api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}`
- `GET /api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}`

## Response Shape

All responses use:

```json
{
  "success": true,
  "data": {},
  "error": null,
  "meta": {
    "api_version": "v3",
    "timestamp": "2026-04-08T04:30:00Z",
    "request_id": "...",
    "duration_ms": 12
  }
}
```

### Single Region Example

```json
{
  "success": true,
  "data": {
    "code": 110101,
    "short_code": "11/01/01",
    "name": "BAKONGAN",
    "depth": 3,
    "type": "district",
    "has_children": true,
    "parent": {
      "code": 1101,
      "short_code": "11/01",
      "name": "ACEH SELATAN",
      "depth": 2,
      "type": "regency",
      "parent": {
        "code": 11,
        "short_code": "11",
        "name": "ACEH",
        "depth": 1,
        "type": "province",
        "parent": null
      }
    }
  },
  "error": null,
  "meta": {
    "api_version": "v3",
    "timestamp": "2026-04-08T04:30:00Z",
    "request_id": "...",
    "duration_ms": 11
  }
}
```

### List Example

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "code": 1101,
        "short_code": "11/01",
        "name": "ACEH SELATAN",
        "depth": 2,
        "type": "regency",
        "has_children": true,
        "parent": {
          "code": 11,
          "short_code": "11",
          "name": "ACEH",
          "depth": 1,
          "type": "province",
          "parent": null
        }
      }
    ],
    "pagination": {
      "total": 1,
      "per_page": 1,
      "has_next": false,
      "has_prev": false,
      "next_cursor": null,
      "prev_cursor": null
    }
  },
  "error": null,
  "meta": {
    "api_version": "v3",
    "timestamp": "2026-04-08T04:30:00Z",
    "request_id": "...",
    "duration_ms": 9
  }
}
```

## Run Locally

```bash
uv sync
uv run fastapi dev app/main.py
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

## Tests

```bash
uv run --group dev pytest tests -q
```

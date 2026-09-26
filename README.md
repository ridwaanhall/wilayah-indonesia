# Wilayah Indonesia API

Free JSON API for Indonesian administrative region codes: 38 provinces, 514 regencies and cities,
7,277 districts and 83,731 villages, each with its full parent chain. No API key.

- Live demo: <https://wilayah.rone.dev>
- Swagger UI: <https://wilayah.rone.dev/docs>
- Error codes: <https://wilayah.rone.dev/docs/errors>
- Hosted API terms: [HOSTED_API_TERMS.md](HOSTED_API_TERMS.md)

```bash
curl https://wilayah.rone.dev/api/kode/3301012001
```

## The demo site

The landing page at `/` is a working client for the API, not a brochure:

- **Explorer**: four cascading pickers (provinsi → kabupaten/kota → kecamatan → desa/kelurahan)
  with type-to-filter, full keyboard support and shareable `?kode=` deep links.
- **Jump to a code**: accepts full codes (`3301012001`) or shorthand (`33/01/01/2001`, `33.1.1.2001`)
  and shows the API's own error envelope when the code is wrong.
- **Request log**: every call the page makes is listed with status and timing; select one to read its JSON.
- **Analytics**: totals, kabupaten/kota and desa/kelurahan splits, and a ranking of child regions for
  whatever is selected, all from `GET /api/stats/{kode}`. Select a row to drill down.
- **Reference**: generated from the registered routes, so it cannot drift from the API.

It is server-rendered with Jinja2 and uses one hand-written stylesheet and one ES module.
There is no build step and no frontend dependency.

## Endpoints

All endpoints are `GET`.

| Path | Returns |
| --- | --- |
| `/api/` | API index: version, docs links, endpoints grouped by tag |
| `/api/health` | Health check |
| `/api/0` | All provinces |
| `/api/{kode_provinsi}` | Regencies and cities in a province, e.g. `/api/33` |
| `/api/{kode_provinsi}/{kode_kabupaten}` | Districts in a regency, e.g. `/api/33/3301` |
| `/api/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}` | Villages in a district, e.g. `/api/33/3301/330101` |
| `/api/kode/{kode}` | Any region by full code (2, 4, 6 or 10 digits) |
| `/api/s/{prov}/{kab}/{kec}/{desa}` | Shorthand lookup, 1 to 4 segments, e.g. `/api/s/33/1/1/2001` |
| `/api/stats/{kode}` | Descendant totals for a region and each direct child; `0` means Indonesia |

Query parameter `parent`:

- Lookups (`/api/kode`, `/api/s`) default to `parent=true` and return the full chain up to the province.
- Lists default to `parent=false`; `parent=true` adds each item's direct parent only.

Other routes: `/` (demo), `/docs/errors` (error catalog), `/docs`, `/redoc`, `/openapi.json`,
`/robots.txt`, `/sitemap.xml`.

## Codes and kinds

Full codes grow by level: `33` → `3301` → `330101` → `3301012001`. `short_code` splits them as
`33/01/01/2001`.

`/api/stats` also splits regions by kind, following the official code convention rather than names:

- Regency segment `71`–`99` is a **kota**, anything lower a **kabupaten**
  (`KOTAWARINGIN BARAT` is a kabupaten).
- The first digit of a village segment is `1` for **kelurahan**, `2` for **desa**, `3` for **desa adat**.

## Response envelope

Every response, success or error, has the same shape:

```json
{
  "success": true,
  "data": {
    "code": 330101,
    "short_code": "33/01/01",
    "name": "KEDUNGREJA",
    "depth": 3,
    "type": "district",
    "has_children": true,
    "parent": {
      "code": 3301,
      "short_code": "33/01",
      "name": "CILACAP",
      "depth": 2,
      "type": "regency",
      "parent": { "code": 33, "short_code": "33", "name": "JAWA TENGAH", "depth": 1, "type": "province", "parent": null }
    }
  },
  "error": null,
  "meta": { "api_version": "v3", "timestamp": "2026-04-08T04:30:00Z", "request_id": "…", "duration_ms": 3 }
}
```

Lists put their items in `data.items` with a `data.pagination` block (lists are always complete).
Stats return `data.levels`, `data.kinds` and `data.children`.

Errors set `success` to `false` and fill `error`:

```json
{
  "code": "INVALID_REGION_CODE",
  "message": "The region code format is invalid.",
  "detail": "Parameter kode must use one of the supported code lengths: 2 (province), 4 (regency), 6 (district), or 10 (village).",
  "hint": "Use 2 digits for a province, 4 for a regency, 6 for a district, or 10 for a village.",
  "docs": "https://wilayah.rone.dev/docs/errors#INVALID_REGION_CODE",
  "fields": [{ "field": "kode", "value": 123, "rule": "digits:2|4|6|10", "message": "kode must be 2, 4, 6, or 10 digits." }]
}
```

Branch on `error.code`; the full list is at [`/docs/errors`](https://wilayah.rone.dev/docs/errors).

## Run locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run fastapi dev app/main.py
```

Then open <http://127.0.0.1:8000/>. On Windows consoles that cannot print emoji, run
`uv run uvicorn app.main:app --reload` instead.

Settings come from environment variables or `.env`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SITE_URL` | `https://wilayah.rone.dev` | Canonical URL for SEO tags, `robots.txt` and `sitemap.xml` |
| `ALLOWED_ORIGINS` | empty | Comma-separated CORS origins; CORS is off when empty |
| `DEBUG` | `false` | FastAPI debug mode |

## Tests

```bash
uv run --group dev pytest tests -q
```

## Data

The dataset lives in [`data/`](data) as four JSON files. If you need all of it, take the files
instead of crawling the API. The data is a snapshot of the official register, not a live mirror;
see [HOSTED_API_TERMS.md](HOSTED_API_TERMS.md).

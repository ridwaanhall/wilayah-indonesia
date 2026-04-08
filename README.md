# Wilayah Indonesia API

Layanan API wilayah administratif Indonesia berbasis FastAPI dengan namespace standar /api, struktur proyek profesional, dan dukungan shorthand endpoint melalui /api/s.

## Ringkasan

- Runtime dependency menggunakan fastapi[standard]
- Dependency management menggunakan uv dengan pyproject.toml dan uv.lock
- Arsitektur OOP dan DRY pada service layer
- Dokumentasi OpenAPI dibagi dalam grup root, search, wilayah, dan simple
- Seluruh endpoint memakai envelope respons standar: success, data, error, meta
- Endpoint simple menggunakan namespace /api/s hingga level desa/kelurahan (level 4)

## Endpoint Namespace

Semua endpoint data berada di bawah prefix /api.

### root

- GET /api/

### search

- GET /api/kode/{kode}

### wilayah (kode penuh)

- GET /api/0
- GET /api/{kode_provinsi}
- GET /api/{kode_provinsi}/{kode_kabupaten}
- GET /api/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}

Catatan:

- Query parent=true tetap didukung pada endpoint list wilayah level 2 sampai 4.

### simple (shorthand)

- GET /api/s/{kode_provinsi}
- GET /api/s/{kode_provinsi}/{nomor_kabupaten}
- GET /api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}
- GET /api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}

Contoh:

- /api/s/11/1/1 akan diproses menjadi kode lengkap 110101
- Respons tetap menampilkan kode_singkat sebagai format dua digit: 11/01/01

## Standar Respons API

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
    "request_id": "01HZ9QXMBF3RVTKNE8D4J7WQCX",
    "duration_ms": 12
  }
}
```

Aturan tingkat pada simple endpoint:

- tingkat 1: provinsi
- tingkat 2: kabupaten/kota
- tingkat 3: kecamatan
- tingkat 4: desa/kelurahan

## Standar Respons Error

Untuk error, API selalu mengembalikan envelope yang sama (`success=false`, `data=null`, `error`, `meta`).

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "REGION_NOT_FOUND",
    "message": "The requested region could not be found.",
    "detail": "No region with code 330999 exists in the national reference dataset.",
    "hint": "Verify the region code using GET /api/0 for valid province codes.",
    "docs": "https://api.yourapp.com/docs/errors#REGION_NOT_FOUND",
    "fields": null
  },
  "meta": {
    "api_version": "v3",
    "timestamp": "2026-04-08T04:30:00Z",
    "request_id": "01HZ9U00000000000000000000",
    "duration_ms": 4
  }
}
```

## Menjalankan Proyek

### Sinkronisasi dependency

```bash
uv sync
```

### Menjalankan server development

```bash
uv run fastapi dev app/main.py
```

Alternatif:

```bash
fastapi dev
```

Server default: <http://127.0.0.1:8000>

## Dokumentasi API

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

Simple endpoint sudah memiliki contoh respons langsung pada OpenAPI untuk tingkat 1, 2, 3, dan 4.

## Testing

```bash
uv run --group dev pytest tests -q
```

## Struktur Proyek

```text
wilayah-indonesia/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   ├── examples.py
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── root.py
│   │       ├── search.py
│   │       ├── wilayah.py
│   │       └── simple.py
│   ├── core/
│   │   ├── config.py
│   │   └── http.py
│   ├── schemas/
│   │   ├── common.py
│   │   └── wilayah.py
│   ├── services/
│   │   ├── data_loader.py
│   │   ├── simple.py
│   │   └── wilayah.py
│   └── main.py
├── api/
│   └── main.py
├── data/
├── tests/
├── pyproject.toml
├── uv.lock
├── vercel.json
└── README.md
```

## Deployment

Entrypoint kompatibilitas api/main.py tetap dipertahankan untuk deployment yang mengacu ke api.main:app.

## License

MIT

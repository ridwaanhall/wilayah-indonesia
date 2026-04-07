# Wilayah Indonesia API

Layanan API wilayah administratif Indonesia berbasis FastAPI dengan namespace standar /api, struktur proyek profesional, dan dukungan shorthand endpoint melalui /api/s.

## Ringkasan

- Runtime dependency menggunakan fastapi[standard]
- Dependency management menggunakan uv dengan pyproject.toml dan uv.lock
- Arsitektur OOP dan DRY pada service layer
- Dokumentasi OpenAPI dibagi dalam grup root, search, wilayah, dan simple
- Endpoint simple menggunakan namespace /api/s dengan respons terstandar

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

Contoh:

- /api/s/11/1/1 akan diproses menjadi kode lengkap 110101
- Respons tetap menampilkan kode_singkat sebagai format dua digit: 11/01/01

## Standar Respons Simple

```json
{
  "success": true,
  "message": "Data kecamatan berhasil ditemukan.",
  "data": {
    "kode_lengkap": 110101,
    "kode_singkat": "11/01/01",
    "kode": 110101,
    "nama": "BAKONGAN",
    "tingkat": 3,
    "level": "kecamatan",
    "parent": {
      "kode": 1101,
      "nama": "KABUPATEN ACEH SELATAN",
      "tingkat": 2
    }
  }
}
```

Aturan tingkat pada simple endpoint:

- tingkat 1: provinsi
- tingkat 2: kabupaten/kota
- tingkat 3: kecamatan

## Standar Respons Error

Untuk data yang tidak ditemukan, API menggunakan pesan profesional dan konsisten:

```json
{
  "detail": "Data wilayah yang diminta tidak ditemukan. Pastikan kode wilayah benar dan tersedia pada dataset resmi."
}
```

Untuk validasi parameter yang tidak sesuai:

```json
{
  "detail": "Parameter permintaan tidak valid. Periksa kembali format dan nilai kode wilayah yang dikirim."
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

Simple endpoint sudah memiliki contoh respons langsung pada OpenAPI untuk tingkat 1, 2, dan 3.

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

# Wilayah Indonesia API

Public API untuk data wilayah administratif Indonesia berbasis FastAPI, dengan struktur proyek modern, endpoint hierarki lama (compatible), serta endpoint simple untuk kode ringkas.

## Highlights

- Menggunakan FastAPI standard stack melalui satu dependency utama: `fastapi[standard]`
- Dependency dikelola dengan `uv` (`pyproject.toml` + `uv.lock`)
- Struktur proyek layer-based: `api`, `services`, `schemas`, `core`
- Dokumentasi OpenAPI terpisah per grup endpoint: `root`, `search`, `wilayah`, `simple`
- Dukungan shorthand code, misalnya `11/01/01` untuk kecamatan `110101`

## Endpoint Groups

### root

- `GET /`

### search

- `GET /kode/{kode}`

### wilayah (aturan lama)

- `GET /0`
- `GET /{kode_provinsi}`
- `GET /{kode_provinsi}/{kode_kabupaten}`
- `GET /{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}`

Catatan:
- `parent=true` tetap didukung pada endpoint list wilayah level 2, 3, dan 4.

### simple (aturan ringkas)

- `GET /simple/{kode_provinsi}`
- `GET /simple/{kode_provinsi}/{nomor_kabupaten}`
- `GET /simple/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}`

Alias kompatibilitas juga tersedia pada jalur lama:
- `GET /{kode_provinsi}/{nomor_kabupaten}`
- `GET /{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}`

Contoh:
- `11/1101/110101` (format lama)
- `11/01/01` (format simple)

## Standar Respons Simple

Endpoint simple memakai respons terstruktur:

```json
{
  "success": true,
  "message": "Data kecamatan berhasil ditemukan.",
  "data": {
    "kode_lengkap": "110101",
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

Aturan tingkat:

- `tingkat=1` untuk `provinsi`
- `tingkat=2` untuk `kabupaten/kota`
- `tingkat=3` untuk `kecamatan`

## Menjalankan Proyek (uv + fastapi)

### 1. Sinkronisasi dependency

```bash
uv sync
```

### 2. Jalankan server development

```bash
uv run fastapi dev app/main.py
```

Atau, jika ingin langsung:

```bash
fastapi dev app/main.py
```

API akan aktif di `http://127.0.0.1:8000`.

## Dokumentasi API

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Testing

```bash
uv run pytest -v
```

## Struktur Proyek

```text
wilayah-indonesia/
├── app/
│   ├── api/
│   │   ├── deps.py
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
│   │   └── simple.py
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

`api/main.py` tetap disediakan sebagai compatibility entrypoint untuk platform yang masih mengacu ke `api.main:app`.

## License

MIT

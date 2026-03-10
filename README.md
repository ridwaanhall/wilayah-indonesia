# API Wilayah Indonesia

A public REST API serving complete Indonesian administrative region data — provinces, regencies/cities, districts, and villages — built with FastAPI.

## Endpoints

| Endpoint | Description | Example |
|---|---|---|
| `/` | API root | |
| `/0` | List all provinces | |
| `/{kode_provinsi}` | List regencies/cities in a province | `/11` (Aceh) |
| `/{kode_provinsi}/{kode_kabupaten}` | List districts in a regency/city | `/11/1101` |
| `/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}` | List villages in a district | `/11/1101/110101` |

## Response Format

All endpoints return JSON.

```json
[
  {
    "kode": 11,
    "nama": "ACEH",
    "tingkat": 1
  },
  {
    "kode": 12,
    "nama": "SUMATERA UTARA",
    "tingkat": 1
  }
]
```

## Data Coverage

| Level | Indonesian Term | Count |
|---|---|---|
| Province | Provinsi | 38 |
| Regency/City | Kabupaten/Kota | 514 |
| District | Kecamatan | 7,277 |
| Village | Desa/Kelurahan | 83,731 |

## Tech Stack

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic
- Vercel (deployment)

## Local Development

```bash
# Clone and install
git clone https://github.com/ridwaanhall/wilayah-indonesia.git
cd wilayah-indonesia
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Start server
uvicorn api.main:app --reload
```

The API is available at `http://127.0.0.1:8000/`.

Interactive docs available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Project Structure

```
api/
  __init__.py
  main.py       # FastAPI app, middleware, error handlers
  config.py     # Settings from environment variables
  loader.py     # JSON data loader with singleton pattern
  routes.py     # API endpoint handlers
  schemas.py    # Pydantic response models
data/
  provinsi.json
  kabupaten.json
  kecamatan.json
  desa.json
```

## License

MIT

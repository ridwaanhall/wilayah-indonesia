# API Wilayah Indonesia

A public REST API serving complete Indonesian administrative region data — provinces, regencies/cities, districts, and villages — built with Django REST Framework.

## Endpoints

| Endpoint | Description | Example |
|---|---|---|
| `/` | API root | |
| `/0/` | List all provinces | |
| `/{kode_provinsi}/` | List regencies/cities in a province | `/11/` (Aceh) |
| `/{kode_provinsi}/{kode_kabupaten}/` | List districts in a regency/city | `/11/1101/` |
| `/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}/` | List villages in a district | `/11/1101/110101/` |

## Response Format

All endpoints return JSON by default. A browsable HTML interface is available when accessed from a browser.

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

- Python 3.13
- Django 6.0
- Django REST Framework 3.16
- WhiteNoise (static files)
- Vercel (deployment)

## Local Development

```bash
# Clone and install
git clone https://github.com/your-username/wilayah-indonesia.git
cd wilayah-indonesia
python -m venv .venv
.venv/Scripts/activate  # Windows
pip install -r requirements.txt

# Set DEBUG=True in .env
echo DEBUG=True > .env

# Run migrations and load data
python manage.py migrate
python manage.py add_province
python manage.py add_regency
python manage.py add_district
python manage.py add_village

# Start server
python manage.py runserver
```

The API is available at `http://localhost:8000/api/` in development mode.

## Management Commands

| Command | Description |
|---|---|
| `add_province` | Import provinces from `ppwp/0.json` |
| `add_regency` | Import regencies from `ppwp/<kode>.json` |
| `add_district` | Import districts from `ppwp/<kode>/<kode>.json` |
| `add_village` | Import villages from `ppwp/<kode>/<kode>/<kode>.json` |
| `extract_province` | Export provinces to `apps/wilayah/data/provinsi.json` |
| `extract_regency` | Export regencies to `apps/wilayah/data/kabupaten.json` |
| `extract_district` | Export districts to `apps/wilayah/data/kecamatan.json` |
| `extract_village` | Export villages to `apps/wilayah/data/desa.json` |

## License

MIT

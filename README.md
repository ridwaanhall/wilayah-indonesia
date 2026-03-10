# API Wilayah Indonesia

A public REST API serving complete Indonesian administrative region data with hierarchical parent information. Built with FastAPI, providing data for provinces, regencies/cities, districts, and villages.

## Features

- Complete hierarchical data for all Indonesian administrative regions
- Optional parent information for each region level
- Fast O(1) lookups with in-memory indexing
- RESTful API with comprehensive OpenAPI documentation
- Single-region search by code
- CORS support for web applications

## API Endpoints

### Root and Information

| Endpoint | Description | Example |
|---|---|---|
| `/` | API root with version and documentation links | |
| `/docs` | Interactive Swagger UI documentation | |
| `/redoc` | ReDoc API documentation | |

### Region Listing

| Endpoint | Description | Query Parameters | Example |
|---|---|---|---|
| `/0` | List all provinces | - | `/0` |
| `/{kode_provinsi}` | List regencies/cities in a province | `parent` (boolean, default: false) | `/11` or `/11?parent=true` |
| `/{kode_provinsi}/{kode_kabupaten}` | List districts in a regency/city | `parent` (boolean, default: false) | `/11/1101?parent=true` |
| `/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}` | List villages in a district | `parent` (boolean, default: false) | `/11/1101/110101?parent=true` |

### Search by Code

| Endpoint | Description | Example |
|---|---|---|
| `/kode/{kode}` | Search for any region by its unique code | `/kode/3401` |

## Query Parameters

### `parent` Parameter

The `parent` query parameter controls whether parent region information is included in responses:

- `parent=false` (default): Returns regions without parent information
- `parent=true`: Includes full parent region details (kode, nama, tingkat)

**Examples:**

```bash
# Without parent info (default)
GET /34
# Returns: [{"kode": 3401, "nama": "KULON PROGO", "tingkat": 2, "parent": null}, ...]

# With parent info
GET /34?parent=true
# Returns: [{"kode": 3401, "nama": "KULON PROGO", "tingkat": 2,
#           "parent": {"kode": 34, "nama": "DAERAH ISTIMEWA YOGYAKARTA", "tingkat": 1}}, ...]
```

## Response Format

All endpoints return JSON. Administrative regions have the following structure:

### Province (tingkat: 1)
```json
{
  "kode": 34,
  "nama": "DAERAH ISTIMEWA YOGYAKARTA",
  "tingkat": 1
}
```

### Regency/City (tingkat: 2)
```json
{
  "kode": 3401,
  "nama": "KULON PROGO",
  "tingkat": 2,
  "parent": {
    "kode": 34,
    "nama": "DAERAH ISTIMEWA YOGYAKARTA",
    "tingkat": 1
  }
}
```

### District (tingkat: 3)
```json
{
  "kode": 340101,
  "nama": "TEMON",
  "tingkat": 3,
  "parent": {
    "kode": 3401,
    "nama": "KULON PROGO",
    "tingkat": 2
  }
}
```

### Village (tingkat: 4)
```json
{
  "kode": 3401012001,
  "nama": "JANTEN",
  "tingkat": 4,
  "parent": {
    "kode": 340101,
    "nama": "TEMON",
    "tingkat": 3
  }
}
```

Note: The `parent` field is `null` when `parent=false` or omitted.

## Data Coverage

| Level | Indonesian Term | Count |
|---|---|---|
| Province | Provinsi | 38 |
| Regency/City | Kabupaten/Kota | 514 |
| District | Kecamatan | 7,277 |
| Village | Desa/Kelurahan | 83,731 |

## Tech Stack

- Python 3.12+
- FastAPI - Modern web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- Vercel - Serverless deployment

## Local Development

### Installation

```bash
# Clone repository
git clone https://github.com/ridwaanhall/wilayah-indonesia.git
cd wilayah-indonesia

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000/`

### API Documentation

Interactive documentation is available at:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Project Structure

```
wilayah-indonesia/
├── api/
│   ├── __init__.py
│   ├── main.py       # FastAPI app, middleware, error handlers
│   ├── config.py     # Configuration from environment variables
│   ├── loader.py     # JSON data loader with singleton pattern
│   ├── routes.py     # API endpoint handlers
│   └── schemas.py    # Pydantic response models
├── data/
│   ├── provinsi.json     # Province data
│   ├── kabupaten.json    # Regency/city data with parent info
│   ├── kecamatan.json    # District data with parent info
│   └── desa.json         # Village data with parent info
├── tests/
│   ├── test_api.py       # API endpoint tests
│   └── test_loader.py    # Data loader tests
├── requirements.txt
└── README.md
```

## Data Structure

The data files use a hierarchical structure where each region (except provinces) contains parent information:

- **provinsi.json**: Contains all provinces
- **kabupaten.json**: Contains regencies/cities with parent province information
- **kecamatan.json**: Contains districts with parent regency information
- **desa.json**: Contains villages with parent district information

Each child level references its immediate parent, creating a clean hierarchical relationship.

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=term-missing
```

## Usage Examples

### Get all provinces
```bash
curl http://127.0.0.1:8000/0
```

### Get regencies in a province (with parent info)
```bash
curl http://127.0.0.1:8000/11?parent=true
```

### Get districts in a regency (without parent info)
```bash
curl http://127.0.0.1:8000/11/1101
```

### Get villages in a district (with parent info)
```bash
curl http://127.0.0.1:8000/11/1101/110101?parent=true
```

### Search by code
```bash
curl http://127.0.0.1:8000/kode/3401
```

## License

MIT

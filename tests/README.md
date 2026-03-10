# Tests

This directory contains the test suite for the Wilayah Indonesia API.

## Running Tests

To run all tests:

```bash
pytest tests/ -v
```

To run tests with coverage:

```bash
pytest tests/ --cov=api --cov-report=term-missing
```

To run a specific test file:

```bash
pytest tests/test_api.py -v
pytest tests/test_loader.py -v
```

## Test Structure

- `test_api.py`: Tests for all API endpoints, including the new `/kode/{kode}` search endpoint
- `test_loader.py`: Tests for the DataLoader class and data indexing functionality

## Test Coverage

The test suite includes:

- API endpoint tests (root, provinsi, kabupaten, kecamatan, desa, search by code)
- DataLoader functionality tests (singleton pattern, data indexing, search methods)
- Error handling and validation tests
- Response structure validation

# Tests

This directory contains the test suite for the Wilayah Indonesia API.

## Running Tests

To run all tests:

```bash
uv run pytest tests/ -v
```

To run tests with coverage:

```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

To run a specific test file:

```bash
uv run pytest tests/test_api.py -v
uv run pytest tests/test_loader.py -v
```

## Test Structure

- `test_api.py`: Tests for API endpoint groups (`root`, `search`, `wilayah`, `simple`)
- `test_loader.py`: Tests for the DataLoader class and data indexing functionality

## Test Coverage

The test suite includes:

- API endpoint tests (legacy wilayah rules, search by code, and simple shorthand)
- DataLoader functionality tests (singleton pattern, data indexing, search methods)
- Error handling and validation tests
- Response structure validation

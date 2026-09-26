# Tests

```bash
uv run --group dev pytest tests -q
```

- `test_api.py`: every endpoint group (`root`, `search`, `stats`, `wilayah`, `simple`), the demo
  pages, `robots.txt`, `sitemap.xml`, static assets and generic 404/405 errors.
- `test_schema_contracts.py`: success and error payloads validated against the declared Pydantic models.
- `test_loader.py`: the in-memory index, national counts and the kabupaten/kota and desa/kelurahan rules.

# AGENTS.md

Guidance for coding agents working in this repository.

## What this is

A read-only FastAPI service for Indonesian administrative regions (provinsi, kabupaten/kota,
kecamatan, desa/kelurahan), plus a server-rendered demo site at `/`. The whole dataset lives in
`data/*.json`, is loaded once into memory, and never changes at runtime. There is no database.

## Commands

```bash
uv sync                                   # install
uv run fastapi dev app/main.py            # dev server on :8000 (Windows: uv run uvicorn app.main:app --reload)
uv run --group dev pytest tests -q        # tests; run before every commit
```

## Layout

```
app/
  main.py                 create_app(): middleware, handlers, /static mount, routers
  core/
    config.py             Settings (env / .env): SITE_URL, ALLOWED_ORIGINS, DEBUG
    errors.py             ERRORS catalog (single source for codes, statuses, hints) + ApiException
    responses.py          success/list/error envelopes
    http.py               security + cache headers, exception handlers
  services/
    data_loader.py        DataLoader: regions, children, descendant counts; region_kind()
    wilayah.py            WilayahService: every lookup, list, shorthand and stats rule
  api/
    catalog.py            API_PREFIX, public_routes()
    router.py             include order matters (see below)
    deps.py               Service / parent query aliases
    examples.py           OpenAPI examples + shared responses()
    endpoints/            root, search, stats, simple, wilayah
  schemas/                Pydantic response models
  web/
    pages.py              /, /docs/errors, /robots.txt, /sitemap.xml, CSP, asset fingerprints
    templates/            base.html, index.html, errors.html (Jinja2)
    static/               app.css, app.js (no build step)
prod/main.py              Vercel entrypoint (vercel.json routes everything here)
tests/                    pytest suite
```

## Rules that are easy to break

- **Public API contract.** Paths, response shapes, field names and error codes are relied on by
  clients. Additive changes only; never rename or remove a field. Tests pin the contract.
- **Router order.** `wilayah.router` has `/{kode_provinsi}` and must stay registered last, or it
  captures `/kode`, `/stats` and `/s`.
- **Errors come from the catalog.** Raise `ApiException("CODE", detail, fields)`; add new codes to
  `ERRORS` in `app/core/errors.py`. The `/docs/errors` page and every `error.docs` link read from it.
- **Region rules live in `WilayahService`.** Endpoints stay thin. `_resolve_chain` is the one place
  that validates code length and parent membership for lists and shorthand lookups.
- **Kinds are derived from codes, not names.** Regency segment >= 71 is a kota; the village
  segment's first digit is 1 kelurahan, 2 desa, 3 desa adat. See `region_kind()`.
- **Code 0 is Indonesia.** `/api/0` lists provinces and `/api/stats/0` returns national totals.

## Frontend

- Plain Jinja2 + one CSS file + one ES module. No framework, no bundler, no CDN scripts.
- The Content-Security-Policy allows only same-origin scripts and Google Fonts. No inline scripts,
  no inline `style` attributes (set CSS custom properties from JS through `element.style`).
- Colours are tokens on `:root` with a dark-mode override. The three `--series-*` colours were
  checked for colour-blind separation in both modes; re-check them if you change them.
- Level labels are defined once in `LEVEL_LABELS` (`app/web/pages.py`), rendered as `data-*`
  attributes and read back by `app.js`. Do not duplicate them in JavaScript.
- The reference table is generated from `public_routes()` and each path parameter's `examples`.
  A new endpoint shows up automatically; give its path parameters `examples=[...]`.
- Static URLs are fingerprinted by content (`asset_url()`); pages are browser-cached for 5 minutes.
- The demo must keep working at 375px wide with no horizontal scroll, and with the keyboard alone.

## Conventions

- Python 3.12+, type hints everywhere, `Annotated` parameters.
- OpenAPI summaries and descriptions are in Indonesian; the demo site, README and code comments
  are in English.
- Remove code that becomes unused. Prefer one parameterised path over near-copies.
- Commit messages start with an emoji and a conventional type, e.g. `✨feat: …`, `🐛fix: …`, `📝docs: …`.

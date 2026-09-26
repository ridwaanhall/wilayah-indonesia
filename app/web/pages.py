"""Server-rendered pages: the interactive demo, the error catalog, robots.txt and sitemap.xml."""

import hashlib
from functools import cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates

from app.api.catalog import public_routes
from app.core.config import get_settings
from app.core.errors import ERRORS
from app.services.data_loader import LEVEL_TYPES, ROOT_CODE, get_loader

WEB_DIR = Path(__file__).resolve().parent
STATIC_DIR = WEB_DIR / "static"
templates = Jinja2Templates(directory=WEB_DIR / "templates")


@cache
def asset_url(name: str) -> str:
    """Return a static URL fingerprinted by content, so cached copies expire on every change."""
    digest = hashlib.sha256((STATIC_DIR / name).read_bytes()).hexdigest()[:10]
    return f"/static/{name}?v={digest}"


templates.env.globals["asset_url"] = asset_url

LEVEL_LABELS: dict[int, tuple[str, str]] = {
    1: ("Provinsi", "Province"),
    2: ("Kabupaten / Kota", "Regency or city"),
    3: ("Kecamatan", "District"),
    4: ("Desa / Kelurahan", "Village"),
}
# (depth, API type, Indonesian label, English label). Rendered into the page; app.js reads labels back from it.
LEVELS = tuple((depth, level_type, *LEVEL_LABELS[depth]) for depth, level_type in LEVEL_TYPES.items())

PAGE_PATHS = ("/", "/docs/errors")

CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' https://fonts.googleapis.com",
        "font-src https://fonts.gstatic.com",
        "img-src 'self' https://rone.dev data:",
        "connect-src 'self'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    )
)

router = APIRouter(include_in_schema=False)


def _example_path(route: APIRoute) -> str:
    """Fill path parameters with the examples declared on the endpoint itself."""
    examples = {param.name: (param.field_info.examples or [""])[0] for param in route.dependant.path_params}
    return route.path.format(**examples)


def _render(request: Request, name: str, **context: Any) -> HTMLResponse:
    settings = get_settings()
    response = templates.TemplateResponse(
        request=request,
        name=name,
        context={"settings": settings, "site_url": settings.site_url.rstrip("/"), **context},
    )
    response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
    # Browsers revalidate pages quickly so new asset fingerprints are picked up; the CDN keeps them longer.
    response.headers["Cache-Control"] = "public, max-age=300, s-maxage=86400"
    return response


@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request) -> HTMLResponse:
    endpoints = [
        {"path": route.path, "summary": route.summary, "tag": route.tags[0], "example": _example_path(route)}
        for route in public_routes(request.app)
    ]
    return _render(
        request,
        "index.html",
        levels=LEVELS,
        totals=get_loader().counts(ROOT_CODE)["levels"],
        endpoints=endpoints,
    )


@router.get("/docs/errors", response_class=HTMLResponse)
def error_catalog(request: Request) -> HTMLResponse:
    return _render(request, "errors.html", errors=ERRORS)


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots() -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {get_settings().site_url.rstrip('/')}/sitemap.xml\n"


@router.get("/sitemap.xml")
def sitemap() -> Response:
    base = get_settings().site_url.rstrip("/")
    urls = "".join(f"<url><loc>{base}{path}</loc></url>" for path in PAGE_PATHS)
    body = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(body, media_type="application/xml")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.core.http import register_exception_handlers, register_http_middleware
from app.web.pages import STATIC_DIR
from app.web.pages import router as pages_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Indonesian administrative regions, from province (provinsi) through regency or city "
            "(kabupaten/kota) and district (kecamatan) to village (desa/kelurahan)."
        ),
        openapi_tags=[
            {"name": "root", "description": "API index and health check."},
            {"name": "lookup", "description": "Look up any region by its full code."},
            {"name": "stats", "description": "Descendant counts per level and per kind, for analytics."},
            {
                "name": "shorthand",
                "description": "Shorthand lookups by segment: /api/s/{province}/{regency}/{district}/{village}.",
            },
            {"name": "hierarchy", "description": "List the children of a region, one level per path segment."},
        ],
    )

    if settings.allowed_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_methods=["GET"],
            allow_headers=["Accept", "Accept-Language", "Content-Type"],
            max_age=86400,
        )

    register_http_middleware(app)
    register_exception_handlers(app)

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(pages_router)
    app.include_router(api_router)
    return app


app = create_app()

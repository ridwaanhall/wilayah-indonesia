from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.http import register_exception_handlers, register_http_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        debug=settings.DEBUG,
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API data wilayah administratif Indonesia untuk level provinsi, "
            "kabupaten/kota, kecamatan, dan desa/kelurahan."
        ),
        redirect_slashes=True,
        openapi_tags=[
            {"name": "root", "description": "Informasi dasar API pada namespace /api."},
            {"name": "search", "description": "Pencarian wilayah berdasarkan kode penuh pada /api/kode/{kode}."},
            {
                "name": "wilayah",
                "description": "Endpoint hierarki kode penuh pada namespace /api.",
            },
            {
                "name": "simple",
                "description": (
                    "Endpoint shorthand pada /api/s. "
                    "Tingkat 1 = provinsi, tingkat 2 = kabupaten/kota, "
                    "tingkat 3 = kecamatan, tingkat 4 = desa/kelurahan."
                ),
            },
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
    app.include_router(api_router)
    return app


app = create_app()

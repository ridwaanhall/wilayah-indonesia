from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.api.catalog import public_routes
from app.core.config import get_settings
from app.core.responses import success_response
from app.schemas.common import SuccessResponse

router = APIRouter(tags=["root"])


class DocsLinks(BaseModel):
    swagger: str
    redoc: str
    openapi: str


class RootData(BaseModel):
    name: str
    version: str
    docs: DocsLinks
    groups: dict[str, list[str]]


class HealthData(BaseModel):
    status: str
    version: str
    database: str


@router.get(
    "/",
    summary="API Root",
    description="Informasi versi, tautan dokumentasi, dan daftar endpoint per grup.",
    response_model=SuccessResponse[RootData],
)
def api_root(request: Request) -> object:
    base_url = str(request.base_url).rstrip("/")
    groups: dict[str, list[str]] = {}
    for route in public_routes(request.app):
        groups.setdefault(str(route.tags[0]), []).append(route.path)

    payload = {
        "name": request.app.title,
        "version": request.app.version,
        "docs": {
            "swagger": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc",
            "openapi": f"{base_url}/openapi.json",
        },
        "groups": groups,
    }
    return success_response(request, payload)


@router.get(
    "/health",
    summary="Health Check",
    description="Status kesehatan layanan.",
    response_model=SuccessResponse[HealthData],
)
def health_check(request: Request) -> object:
    return success_response(
        request,
        {"status": "ok", "version": get_settings().api_version, "database": "connected"},
    )

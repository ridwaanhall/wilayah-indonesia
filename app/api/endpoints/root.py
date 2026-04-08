from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.responses import success_response
from app.schemas.common import SuccessResponse

router = APIRouter(tags=["root"])


class DocsLinks(BaseModel):
    swagger: str
    redoc: str
    openapi: str


class EndpointGroups(BaseModel):
    root: list[str]
    search: list[str]
    wilayah: list[str]
    simple: list[str]


class RootData(BaseModel):
    name: str
    version: str
    docs: DocsLinks
    groups: EndpointGroups


class HealthData(BaseModel):
    status: str
    version: str
    database: str


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama API dengan informasi versi dan tautan dokumentasi.",
    response_model=SuccessResponse[RootData],
)
def api_root(request: Request) -> object:
    """Return API index and grouped endpoint catalog."""
    base_url = str(request.base_url).rstrip("/")
    payload = {
        "name": request.app.title,
        "version": request.app.version,
        "docs": {
            "swagger": f"{base_url}/docs",
            "redoc": f"{base_url}/redoc",
            "openapi": f"{base_url}/openapi.json",
        },
        "groups": {
            "root": ["/api/"],
            "search": ["/api/kode/{kode}"],
            "wilayah": [
                "/api/0",
                "/api/{kode_provinsi}",
                "/api/{kode_provinsi}/{kode_kabupaten}",
                "/api/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
            ],
            "simple": [
                "/api/s/{kode_provinsi}",
                "/api/s/{kode_provinsi}/{nomor_kabupaten}",
                "/api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
                "/api/s/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}",
            ],
        },
    }
    return success_response(request, payload)


@router.get(
    "/health",
    summary="Health Check",
    description="Endpoint status kesehatan layanan.",
    response_model=SuccessResponse[HealthData],
)
def health_check(request: Request) -> object:
    """Return a standardized health status payload."""
    settings = get_settings()
    return success_response(
        request,
        {
            "status": "ok",
            "version": settings.api_version,
            "database": "connected",
        },
    )

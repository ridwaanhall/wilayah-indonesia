from fastapi import APIRouter, Request

from app.core.responses import success_response
from app.schemas.common import ApiEnvelope

router = APIRouter(tags=["root"])


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama API dengan informasi versi dan tautan dokumentasi.",
    response_model=ApiEnvelope,
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
    response_model=ApiEnvelope,
)
def health_check(request: Request) -> object:
    """Return a standardized health status payload."""
    return success_response(
        request,
        {
            "status": "ok",
            "version": "v3",
            "database": "connected",
        },
    )

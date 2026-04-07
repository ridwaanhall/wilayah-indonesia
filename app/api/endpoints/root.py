from fastapi import APIRouter, Request

router = APIRouter(tags=["root"])


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama API dengan informasi versi dan tautan dokumentasi.",
)
def api_root(request: Request) -> dict[str, object]:
    """Return API index and grouped endpoint catalog."""
    base_url = str(request.base_url).rstrip("/")
    return {
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
            ],
        },
    }

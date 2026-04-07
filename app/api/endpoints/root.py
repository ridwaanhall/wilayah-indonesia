from fastapi import APIRouter, Request

router = APIRouter(tags=["root"])


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama API dengan informasi versi dan tautan dokumentasi.",
)
def api_root(request: Request) -> dict[str, object]:
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
            "root": ["/"],
            "search": ["/kode/{kode}"],
            "wilayah": [
                "/0",
                "/{kode_provinsi}",
                "/{kode_provinsi}/{kode_kabupaten}",
                "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
            ],
            "simple": [
                "/simple/{kode_provinsi}",
                "/simple/{kode_provinsi}/{nomor_kabupaten}",
                "/simple/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
                "alias: /{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
            ],
        },
    }

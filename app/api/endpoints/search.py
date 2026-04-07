"""Search endpoints for direct wilayah code lookup."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, status

from app.api.deps import get_wilayah_service
from app.api.examples import ERROR_NOT_FOUND_EXAMPLE
from app.schemas.common import ErrorResponse
from app.schemas.wilayah import Desa, Kabupaten, Kecamatan, Provinsi
from app.services.wilayah import WilayahService

router = APIRouter(tags=["search"])


@router.get(
    "/kode/{kode}",
    summary="Cari Wilayah berdasarkan Kode",
    description=(
        "Cari data wilayah administratif berdasarkan kode. "
        "Mendukung tingkat provinsi, kabupaten/kota, kecamatan, dan desa/kelurahan."
    ),
    status_code=status.HTTP_200_OK,
    response_model=Provinsi | Kabupaten | Kecamatan | Desa,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Kode wilayah tidak tersedia pada dataset.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        }
    },
)
def search_by_code(
    kode: Annotated[int, Path(gt=0, description="Kode wilayah administratif")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
) -> dict[str, Any]:
    """Search any wilayah level by full numeric code."""
    return service.search_by_code(kode)

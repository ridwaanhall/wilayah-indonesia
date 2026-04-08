"""Search endpoints for direct wilayah code lookup."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.api.deps import get_wilayah_service
from app.api.examples import ERROR_NOT_FOUND_EXAMPLE, ERROR_VALIDATION_EXAMPLE, SIMPLE_REGION_EXAMPLE
from app.core.responses import success_response
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.wilayah import RegionResource
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
    response_model=SuccessResponse[RegionResource],
    responses={
        status.HTTP_200_OK: {
            "description": "Data wilayah berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Kode wilayah tidak tersedia pada dataset.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format kode wilayah tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def search_by_code(
    request: Request,
    kode: Annotated[int, Path(gt=0, description="Kode wilayah administratif")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan hierarki parent penuh pada data wilayah (default true)."),
    ] = True,
) -> object:
    """Search any wilayah level by full numeric code."""
    return success_response(request, service.search_by_code(kode, include_parent=parent))

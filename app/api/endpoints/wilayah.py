"""Wilayah hierarchy endpoints using full administrative codes."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.deps import get_wilayah_service
from app.api.examples import ERROR_NOT_FOUND_EXAMPLE, ERROR_VALIDATION_EXAMPLE
from app.schemas.common import ErrorResponse
from app.schemas.wilayah import Desa, Kabupaten, Kecamatan, Provinsi
from app.services.wilayah import WilayahService

router = APIRouter(tags=["wilayah"])


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    status_code=status.HTTP_200_OK,
    response_model=list[Provinsi],
)
def list_provinsi(
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
) -> list[dict[str, Any]]:
    """List all provinces in Indonesia."""
    return service.list_provinsi()


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota pada provinsi tertentu.",
    status_code=status.HTTP_200_OK,
    response_model=list[Kabupaten],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format kode provinsi tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_kabupaten(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[bool, Query(description="Sertakan parent provinsi")] = False,
) -> list[dict[str, Any]]:
    """List kabupaten/kota by province code."""
    return service.list_kabupaten(kode_provinsi, include_parent=parent)


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}",
    summary="Daftar Kecamatan",
    description="Daftar kecamatan berdasarkan kode provinsi dan kode kabupaten/kota penuh.",
    status_code=status.HTTP_200_OK,
    response_model=list[Kecamatan],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi atau kabupaten/kota tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format kode provinsi/kabupaten tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_kecamatan(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota 4 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[bool, Query(description="Sertakan parent kabupaten")] = False,
) -> list[dict[str, Any]]:
    """List kecamatan by full province and kabupaten codes."""
    return service.list_kecamatan(
        kode_provinsi=kode_provinsi,
        kode_kabupaten=kode_kabupaten,
        include_parent=parent,
    )


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
    summary="Daftar Desa/Kelurahan",
    description="Daftar desa/kelurahan berdasarkan kode hierarki wilayah penuh.",
    status_code=status.HTTP_200_OK,
    response_model=list[Desa],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi, kabupaten/kota, atau kecamatan tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format kode wilayah tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_desa(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota 4 digit")],
    kode_kecamatan: Annotated[int, Path(gt=0, description="Kode kecamatan 6 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[bool, Query(description="Sertakan parent kecamatan")] = False,
) -> list[dict[str, Any]]:
    """List desa by full province, kabupaten, and kecamatan codes."""
    return service.list_desa(
        kode_provinsi=kode_provinsi,
        kode_kabupaten=kode_kabupaten,
        kode_kecamatan=kode_kecamatan,
        include_parent=parent,
    )

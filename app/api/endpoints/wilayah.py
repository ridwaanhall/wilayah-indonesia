"""Wilayah hierarchy endpoints using full administrative codes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.api.deps import get_wilayah_service
from app.api.examples import ERROR_NOT_FOUND_EXAMPLE, ERROR_VALIDATION_EXAMPLE, LIST_REGION_EXAMPLE
from app.core.responses import list_response
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.wilayah import RegionListData
from app.services.wilayah import WilayahService

router = APIRouter(tags=["wilayah"])


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionListData],
    responses={
        status.HTTP_200_OK: {
            "description": "Daftar provinsi berhasil diambil.",
            "content": {"application/json": {"example": LIST_REGION_EXAMPLE}},
        }
    },
)
def list_provinsi(
    request: Request,
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan parent pada setiap item (default false). Untuk provinsi nilai tetap null."),
    ] = False,
) -> object:
    """List all provinces in Indonesia."""
    _ = parent  # Keep query parity with other list endpoints.
    return list_response(request, service.list_provinsi())


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota pada provinsi tertentu.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionListData],
    responses={
        status.HTTP_200_OK: {
            "description": "Daftar kabupaten/kota berhasil diambil.",
            "content": {"application/json": {"example": LIST_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format kode provinsi tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_kabupaten(
    request: Request,
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan parent provinsi pada setiap item (default false)."),
    ] = False,
) -> object:
    """List kabupaten/kota by province code."""
    return list_response(
        request,
        service.list_kabupaten(kode_provinsi, include_parent=parent),
    )


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}",
    summary="Daftar Kecamatan",
    description="Daftar kecamatan berdasarkan kode provinsi dan kode kabupaten/kota penuh.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionListData],
    responses={
        status.HTTP_200_OK: {
            "description": "Daftar kecamatan berhasil diambil.",
            "content": {"application/json": {"example": LIST_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi atau kabupaten/kota tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format kode provinsi/kabupaten tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_kecamatan(
    request: Request,
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota 4 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan parent kabupaten/kota pada setiap item (default false)."),
    ] = False,
) -> object:
    """List kecamatan by full province and kabupaten codes."""
    return list_response(
        request,
        service.list_kecamatan(
            kode_provinsi=kode_provinsi,
            kode_kabupaten=kode_kabupaten,
            include_parent=parent,
        ),
    )


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
    summary="Daftar Desa/Kelurahan",
    description="Daftar desa/kelurahan berdasarkan kode hierarki wilayah penuh.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionListData],
    responses={
        status.HTTP_200_OK: {
            "description": "Daftar desa/kelurahan berhasil diambil.",
            "content": {"application/json": {"example": LIST_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi, kabupaten/kota, atau kecamatan tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format kode wilayah tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def list_desa(
    request: Request,
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota 4 digit")],
    kode_kecamatan: Annotated[int, Path(gt=0, description="Kode kecamatan 6 digit")],
    service: Annotated[WilayahService, Depends(get_wilayah_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan parent kecamatan pada setiap item (default false)."),
    ] = False,
) -> object:
    """List desa by full province, kabupaten, and kecamatan codes."""
    return list_response(
        request,
        service.list_desa(
            kode_provinsi=kode_provinsi,
            kode_kabupaten=kode_kabupaten,
            kode_kecamatan=kode_kecamatan,
            include_parent=parent,
        ),
    )

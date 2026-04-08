"""Simple shorthand endpoints for single wilayah retrieval."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request, status

from app.api.deps import get_simple_service
from app.api.examples import (
    ERROR_NOT_FOUND_EXAMPLE,
    ERROR_VALIDATION_EXAMPLE,
    SIMPLE_REGION_EXAMPLE,
)
from app.core.responses import success_response
from app.schemas.common import ErrorResponse, SuccessResponse
from app.schemas.wilayah import RegionResource
from app.services.simple import SimpleWilayahService

router = APIRouter(prefix="/s", tags=["simple"])


@router.get(
    "/{kode_provinsi}",
    summary="Simple Tingkat 1 (Provinsi)",
    description="Ambil data provinsi berdasarkan kode provinsi 2 digit. Tingkat 1 = provinsi.",
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionResource],
    responses={
        status.HTTP_200_OK: {
            "description": "Data provinsi berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_provinsi(
    request: Request,
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan hierarki parent pada data wilayah (default true)."),
    ] = True,
) -> object:
    """Resolve province from shorthand code."""
    return success_response(request, service.get_provinsi(kode_provinsi, include_parent=parent))


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}",
    summary="Simple Tingkat 2 (Kabupaten/Kota)",
    description=(
        "Ambil data kabupaten/kota dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}. Tingkat 2 = kabupaten/kota."
    ),
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionResource],
    responses={
        status.HTTP_200_OK: {
            "description": "Data kabupaten/kota berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi atau kabupaten/kota tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_kabupaten(
    request: Request,
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[int, Path(ge=1, le=99, description="Nomor kabupaten 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan hierarki parent pada data wilayah (default true)."),
    ] = True,
) -> object:
    """Resolve kabupaten/kota from shorthand code."""
    return success_response(
        request,
        service.get_kabupaten(
            kode_provinsi,
            nomor_kabupaten,
            include_parent=parent,
        ),
    )


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
    summary="Simple Tingkat 3 (Kecamatan)",
    description=(
        "Ambil data kecamatan dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}. "
        "Tingkat 3 = kecamatan."
    ),
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionResource],
    responses={
        status.HTTP_200_OK: {
            "description": "Data kecamatan berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi, kabupaten/kota, atau kecamatan tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_kecamatan(
    request: Request,
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[int, Path(ge=1, le=99, description="Nomor kabupaten 2 digit")],
    nomor_kecamatan: Annotated[int, Path(ge=1, le=99, description="Nomor kecamatan 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan hierarki parent pada data wilayah (default true)."),
    ] = True,
) -> object:
    """Resolve kecamatan from shorthand code."""
    return success_response(
        request,
        service.get_kecamatan(
            kode_provinsi,
            nomor_kabupaten,
            nomor_kecamatan,
            include_parent=parent,
        ),
    )


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}",
    summary="Simple Tingkat 4 (Desa/Kelurahan)",
    description=(
        "Ambil data desa/kelurahan dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}. "
        "Tingkat 4 = desa/kelurahan."
    ),
    status_code=status.HTTP_200_OK,
    response_model=SuccessResponse[RegionResource],
    responses={
        status.HTTP_200_OK: {
            "description": "Data desa/kelurahan berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_REGION_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Wilayah referensi tidak ditemukan pada hierarki yang diberikan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_desa(
    request: Request,
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[int, Path(ge=1, le=99, description="Nomor kabupaten 2 digit")],
    nomor_kecamatan: Annotated[int, Path(ge=1, le=99, description="Nomor kecamatan 2 digit")],
    nomor_desa: Annotated[int, Path(ge=1, le=9999, description="Nomor desa 4 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[
        bool,
        Query(description="Sertakan hierarki parent pada data wilayah (default true)."),
    ] = True,
) -> object:
    """Resolve desa/kelurahan from shorthand code."""
    return success_response(
        request,
        service.get_desa(
            kode_provinsi=kode_provinsi,
            nomor_kabupaten=nomor_kabupaten,
            nomor_kecamatan=nomor_kecamatan,
            nomor_desa=nomor_desa,
            include_parent=parent,
        ),
    )

"""Simple shorthand endpoints for single wilayah retrieval."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.deps import get_simple_service
from app.api.examples import (
    ERROR_NOT_FOUND_EXAMPLE,
    ERROR_VALIDATION_EXAMPLE,
    SIMPLE_KABUPATEN_EXAMPLE,
    SIMPLE_KECAMATAN_EXAMPLE,
    SIMPLE_PROVINSI_EXAMPLE,
)
from app.schemas.common import ErrorResponse
from app.schemas.wilayah import SimpleWilayahResponse
from app.services.simple import SimpleWilayahService

router = APIRouter(prefix="/s", tags=["simple"])


@router.get(
    "/{kode_provinsi}",
    summary="Simple Tingkat 1 (Provinsi)",
    description="Ambil data provinsi berdasarkan kode provinsi 2 digit. Tingkat 1 = provinsi.",
    status_code=status.HTTP_200_OK,
    response_model=SimpleWilayahResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Data provinsi berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_PROVINSI_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_provinsi(
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    """Resolve province from shorthand code."""
    return service.get_provinsi(kode_provinsi)


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}",
    summary="Simple Tingkat 2 (Kabupaten/Kota)",
    description=(
        "Ambil data kabupaten/kota dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}. Tingkat 2 = kabupaten/kota."
    ),
    status_code=status.HTTP_200_OK,
    response_model=SimpleWilayahResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Data kabupaten/kota berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_KABUPATEN_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi atau kabupaten/kota tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_kabupaten(
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[int, Path(ge=1, le=99, description="Nomor kabupaten 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    """Resolve kabupaten/kota from shorthand code."""
    return service.get_kabupaten(kode_provinsi, nomor_kabupaten)


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
    summary="Simple Tingkat 3 (Kecamatan)",
    description=(
        "Ambil data kecamatan dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}. "
        "Tingkat 3 = kecamatan."
    ),
    status_code=status.HTTP_200_OK,
    response_model=SimpleWilayahResponse,
    responses={
        status.HTTP_200_OK: {
            "description": "Data kecamatan berhasil ditemukan.",
            "content": {"application/json": {"example": SIMPLE_KECAMATAN_EXAMPLE}},
        },
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Provinsi, kabupaten/kota, atau kecamatan tidak ditemukan.",
            "content": {"application/json": {"example": ERROR_NOT_FOUND_EXAMPLE}},
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Format parameter tidak valid.",
            "content": {"application/json": {"example": ERROR_VALIDATION_EXAMPLE}},
        },
    },
)
def simple_kecamatan(
    kode_provinsi: Annotated[int, Path(ge=1, le=99, description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[int, Path(ge=1, le=99, description="Nomor kabupaten 2 digit")],
    nomor_kecamatan: Annotated[int, Path(ge=1, le=99, description="Nomor kecamatan 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    """Resolve kecamatan from shorthand code."""
    return service.get_kecamatan(kode_provinsi, nomor_kabupaten, nomor_kecamatan)

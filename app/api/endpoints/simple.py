from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.deps import get_simple_service
from app.schemas.wilayah import SimpleWilayahResponse
from app.services.simple import SimpleWilayahService

router = APIRouter(prefix="/simple", tags=["simple"])


@router.get(
    "/{kode_provinsi}",
    summary="Simple Tingkat 1 (Provinsi)",
    description="Ambil data provinsi berdasarkan kode provinsi 2 digit. Tingkat 1 = provinsi.",
    response_model=SimpleWilayahResponse,
)
def simple_provinsi(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    return service.get_provinsi(kode_provinsi)


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}",
    summary="Simple Tingkat 2 (Kabupaten/Kota)",
    description=(
        "Ambil data kabupaten/kota dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}. Tingkat 2 = kabupaten/kota."
    ),
    response_model=SimpleWilayahResponse,
)
def simple_kabupaten(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[str, Path(description="Nomor kabupaten 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    return service.get_kabupaten(kode_provinsi, nomor_kabupaten)


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
    summary="Simple Tingkat 3 (Kecamatan)",
    description=(
        "Ambil data kecamatan dengan format sederhana: "
        "{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}. "
        "Tingkat 3 = kecamatan."
    ),
    response_model=SimpleWilayahResponse,
)
def simple_kecamatan(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    nomor_kabupaten: Annotated[str, Path(description="Nomor kabupaten 2 digit")],
    nomor_kecamatan: Annotated[str, Path(description="Nomor kecamatan 2 digit")],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
) -> SimpleWilayahResponse:
    return service.get_kecamatan(kode_provinsi, nomor_kabupaten, nomor_kecamatan)

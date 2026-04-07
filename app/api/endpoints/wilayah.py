from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.api.deps import get_simple_service
from app.schemas.common import ErrorDetail
from app.schemas.wilayah import Desa, Kabupaten, Kecamatan, Provinsi, SimpleWilayahResponse
from app.services.data_loader import DataLoader, get_loader
from app.services.simple import SimpleWilayahService

router = APIRouter(tags=["wilayah"])


def _require_digits(name: str, value: str, expected_length: int) -> int:
    if not value.isdigit() or len(value) != expected_length:
        raise HTTPException(
            status_code=422,
            detail=f"{name} harus berupa {expected_length} digit angka.",
        )
    return int(value)


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    response_model=list[Provinsi],
)
def list_provinsi(
    loader: Annotated[DataLoader, Depends(get_loader)],
) -> list[dict[str, Any]]:
    return loader.provinsi_list


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota pada provinsi tertentu.",
    response_model=list[Kabupaten],
    responses={404: {"model": ErrorDetail}},
)
def list_kabupaten(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    loader: Annotated[DataLoader, Depends(get_loader)],
    parent: Annotated[bool, Query(description="Sertakan parent provinsi")]=False,
) -> list[dict[str, Any]]:
    kode_provinsi_int = _require_digits("kode_provinsi", kode_provinsi, 2)
    result = loader.kabupaten_by_provinsi(kode_provinsi_int, include_parent=parent)
    if result is None:
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    return result


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}",
    summary="Daftar Kecamatan atau Simple Tingkat 2",
    description=(
        "Mode wilayah lama: gunakan kode_kabupaten 4 digit untuk daftar kecamatan. "
        "Mode simple: gunakan nomor_kabupaten 2 digit untuk data tunggal kabupaten/kota."
    ),
    response_model=list[Kecamatan] | SimpleWilayahResponse,
    responses={404: {"model": ErrorDetail}},
)
def list_kecamatan_or_simple_kabupaten(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[str, Path(description="Kode kabupaten 4 digit atau nomor kabupaten 2 digit")],
    loader: Annotated[DataLoader, Depends(get_loader)],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[bool, Query(description="Sertakan parent kabupaten")]=False,
) -> list[dict[str, Any]] | SimpleWilayahResponse:
    if len(kode_kabupaten) == 2 and kode_kabupaten.isdigit():
        return service.get_kabupaten(kode_provinsi, kode_kabupaten)

    kode_provinsi_int = _require_digits("kode_provinsi", kode_provinsi, 2)
    kode_kabupaten_int = _require_digits("kode_kabupaten", kode_kabupaten, 4)

    if not loader.provinsi_exists(kode_provinsi_int):
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    if not loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
        raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")

    return loader.kecamatan_by_kabupaten(
        kode_kabupaten_int,
        kode_provinsi=kode_provinsi_int,
        include_parent=parent,
    ) or []


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
    summary="Daftar Desa atau Simple Tingkat 3",
    description=(
        "Mode wilayah lama: gunakan format lengkap 2/4/6 digit, misal 11/1101/110101. "
        "Mode simple: gunakan format 2/2/2 digit, misal 11/01/01."
    ),
    response_model=list[Desa] | SimpleWilayahResponse,
    responses={404: {"model": ErrorDetail}},
)
def list_desa_or_simple_kecamatan(
    kode_provinsi: Annotated[str, Path(description="Kode provinsi 2 digit")],
    kode_kabupaten: Annotated[str, Path(description="Kode kabupaten 4 digit atau nomor kabupaten 2 digit")],
    kode_kecamatan: Annotated[str, Path(description="Kode kecamatan 6 digit atau nomor kecamatan 2 digit")],
    loader: Annotated[DataLoader, Depends(get_loader)],
    service: Annotated[SimpleWilayahService, Depends(get_simple_service)],
    parent: Annotated[bool, Query(description="Sertakan parent kecamatan")]=False,
) -> list[dict[str, Any]] | SimpleWilayahResponse:
    if (
        len(kode_kabupaten) == 2
        and len(kode_kecamatan) == 2
        and kode_kabupaten.isdigit()
        and kode_kecamatan.isdigit()
    ):
        return service.get_kecamatan(kode_provinsi, kode_kabupaten, kode_kecamatan)

    kode_provinsi_int = _require_digits("kode_provinsi", kode_provinsi, 2)
    kode_kabupaten_int = _require_digits("kode_kabupaten", kode_kabupaten, 4)
    kode_kecamatan_int = _require_digits("kode_kecamatan", kode_kecamatan, 6)

    if not loader.provinsi_exists(kode_provinsi_int):
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    if not loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
        raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")
    if not loader.kecamatan_in_kabupaten(kode_kecamatan_int, kode_kabupaten_int):
        raise HTTPException(status_code=404, detail="Kecamatan tidak ditemukan.")

    return loader.desa_by_kecamatan(
        kode_kecamatan_int,
        kode_kabupaten=kode_kabupaten_int,
        include_parent=parent,
    ) or []

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Request

from .loader import loader
from .schemas import Desa, ErrorDetail, Kabupaten, Kecamatan, Provinsi

router = APIRouter()


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama yang menampilkan daftar sumber data API.",
)
def api_root(request: Request) -> dict[str, str]:
    base_url: str = str(request.base_url).rstrip("/")
    return {"daftar-provinsi": f"{base_url}/0"}


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    response_model=list[Provinsi],
)
def list_provinsi() -> list[dict]:
    return loader.provinsi_list


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota dalam suatu provinsi.",
    response_model=list[Kabupaten],
    responses={404: {"model": ErrorDetail}},
)
def list_kabupaten(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi")],
) -> list[dict]:
    result: list[dict] | None = loader.kabupaten_by_provinsi(kode_provinsi)
    if result is None:
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    return result


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}",
    summary="Daftar Kecamatan",
    description="Daftar kecamatan dalam suatu kabupaten/kota.",
    response_model=list[Kecamatan],
    responses={404: {"model": ErrorDetail}},
)
def list_kecamatan(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota")],
) -> list[dict]:
    result: list[dict] | None = loader.kecamatan_by_kabupaten(kode_kabupaten)
    if result is None:
        raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")
    return result


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
    summary="Daftar Desa/Kelurahan",
    description="Daftar desa/kelurahan dalam suatu kecamatan.",
    response_model=list[Desa],
    responses={404: {"model": ErrorDetail}},
)
def list_desa(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi")],
    kode_kabupaten: Annotated[int, Path(gt=0, description="Kode kabupaten/kota")],
    kode_kecamatan: Annotated[int, Path(gt=0, description="Kode kecamatan")],
) -> list[dict]:
    result: list[dict] | None = loader.desa_by_kecamatan(kode_kecamatan)
    if result is None:
        raise HTTPException(status_code=404, detail="Kecamatan tidak ditemukan.")
    return result

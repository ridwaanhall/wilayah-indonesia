from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path, Request

from .loader import DataLoader, get_loader
from .schemas import Desa, ErrorDetail, Kabupaten, Kecamatan, Provinsi, WilayahBase

router: APIRouter = APIRouter()

LoaderDep = Annotated[DataLoader, Depends(get_loader)]


@router.get(
    "/",
    summary="API Root",
    description="Endpoint utama yang menampilkan informasi dan dokumentasi API.",
)
def api_root(request: Request) -> dict[str, str | dict[str, str]]:
    base_url: str = str(request.base_url).rstrip("/")
    return {
        "message": "Wilayah Indonesia API",
        "version": "2.0.0",
        "docs": f"{base_url}/docs",
        "endpoints": {
            "provinsi": f"{base_url}/0",
            "search_by_code": f"{base_url}/kode/{{kode}}"
        }
    }


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    response_model=list[Provinsi],
)
def list_provinsi(loader: LoaderDep) -> list[dict[str, Any]]:
    return loader.provinsi_list


@router.get(
    "/kode/{kode}",
    summary="Cari Wilayah berdasarkan Kode",
    description=(
        "Cari data wilayah administratif berdasarkan kode. "
        "Mendukung pencarian untuk semua tingkat: provinsi, kabupaten/kota, "
        "kecamatan, dan desa/kelurahan. Mengembalikan data tunggal."
    ),
    response_model=Provinsi | Kabupaten | Kecamatan | Desa,
    responses={404: {"model": ErrorDetail}},
)
def search_by_code(
    kode: Annotated[int, Path(gt=0, description="Kode wilayah administratif")],
    loader: LoaderDep,
) -> dict[str, Any]:
    result: dict[str, Any] | None = loader.find_by_code(kode)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Kode wilayah tidak ditemukan."
        )
    return result


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota dalam suatu provinsi.",
    response_model=list[Kabupaten],
    responses={404: {"model": ErrorDetail}},
)
def list_kabupaten(
    kode_provinsi: Annotated[int, Path(gt=0, description="Kode provinsi")],
    loader: LoaderDep,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] | None = loader.kabupaten_by_provinsi(kode_provinsi)
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
    loader: LoaderDep,
) -> list[dict[str, Any]]:
    if not loader.provinsi_exists(kode_provinsi):
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    if not loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
        raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")
    return loader.kecamatan_by_kabupaten(kode_kabupaten) or []


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
    loader: LoaderDep,
) -> list[dict[str, Any]]:
    if not loader.provinsi_exists(kode_provinsi):
        raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
    if not loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
        raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")
    if not loader.kecamatan_in_kabupaten(kode_kecamatan, kode_kabupaten):
        raise HTTPException(status_code=404, detail="Kecamatan tidak ditemukan.")
    return loader.desa_by_kecamatan(kode_kecamatan) or []

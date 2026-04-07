from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Path

from app.schemas.common import ErrorDetail
from app.schemas.wilayah import Desa, Kabupaten, Kecamatan, Provinsi
from app.services.data_loader import DataLoader, get_loader

router = APIRouter(tags=["search"])


@router.get(
    "/kode/{kode}",
    summary="Cari Wilayah berdasarkan Kode",
    description=(
        "Cari data wilayah administratif berdasarkan kode. "
        "Mendukung tingkat provinsi, kabupaten/kota, kecamatan, dan desa/kelurahan."
    ),
    response_model=Provinsi | Kabupaten | Kecamatan | Desa,
    responses={404: {"model": ErrorDetail}},
)
def search_by_code(
    kode: Annotated[int, Path(gt=0, description="Kode wilayah administratif")],
    loader: Annotated[DataLoader, Depends(get_loader)],
) -> dict[str, Any]:
    result = loader.find_by_code(kode)
    if result is None:
        raise HTTPException(status_code=404, detail="Kode wilayah tidak ditemukan.")
    return result

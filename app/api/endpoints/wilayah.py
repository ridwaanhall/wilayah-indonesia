"""Hierarchy listings by full codes: /api/0 lists provinces, each extra segment goes one level down."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import ItemParent, Service
from app.api.examples import LIST_EXAMPLE, responses
from app.core.responses import list_response
from app.schemas.common import SuccessResponse
from app.schemas.wilayah import RegionListData

router = APIRouter(
    tags=["wilayah"],
    responses=responses(LIST_EXAMPLE),
)

Provinsi = Annotated[int, Path(gt=0, description="Kode provinsi 2 digit", examples=[33])]
Kabupaten = Annotated[int, Path(gt=0, description="Kode kabupaten/kota 4 digit", examples=[3301])]
Kecamatan = Annotated[int, Path(gt=0, description="Kode kecamatan 6 digit", examples=[330101])]


@router.get(
    "/0",
    summary="Daftar Provinsi",
    description="Daftar seluruh provinsi di Indonesia.",
    response_model=SuccessResponse[RegionListData],
)
def list_provinsi(request: Request, service: Service) -> object:
    return list_response(request, service.list_children([], include_parent=False))


@router.get(
    "/{kode_provinsi}",
    summary="Daftar Kabupaten/Kota",
    description="Daftar kabupaten/kota pada provinsi tertentu.",
    response_model=SuccessResponse[RegionListData],
)
def list_kabupaten(request: Request, kode_provinsi: Provinsi, service: Service, parent: ItemParent = False) -> object:
    return list_response(request, service.list_children([kode_provinsi], include_parent=parent))


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}",
    summary="Daftar Kecamatan",
    description="Daftar kecamatan pada kabupaten/kota tertentu.",
    response_model=SuccessResponse[RegionListData],
)
def list_kecamatan(
    request: Request,
    kode_provinsi: Provinsi,
    kode_kabupaten: Kabupaten,
    service: Service,
    parent: ItemParent = False,
) -> object:
    codes = [kode_provinsi, kode_kabupaten]
    return list_response(request, service.list_children(codes, include_parent=parent))


@router.get(
    "/{kode_provinsi}/{kode_kabupaten}/{kode_kecamatan}",
    summary="Daftar Desa/Kelurahan",
    description="Daftar desa/kelurahan pada kecamatan tertentu.",
    response_model=SuccessResponse[RegionListData],
)
def list_desa(
    request: Request,
    kode_provinsi: Provinsi,
    kode_kabupaten: Kabupaten,
    kode_kecamatan: Kecamatan,
    service: Service,
    parent: ItemParent = False,
) -> object:
    codes = [kode_provinsi, kode_kabupaten, kode_kecamatan]
    return list_response(request, service.list_children(codes, include_parent=parent))

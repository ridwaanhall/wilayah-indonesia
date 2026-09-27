"""Shorthand endpoints: /api/s/33/1/1/2001 resolves to village 3301012001."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import ChainParent, Service
from app.api.examples import REGION_EXAMPLE, responses
from app.core.responses import success_response
from app.schemas.common import SuccessResponse
from app.schemas.wilayah import RegionResource

router = APIRouter(
    prefix="/s",
    tags=["simple"],
    responses=responses(REGION_EXAMPLE),
)

Provinsi = Annotated[int, Path(ge=1, le=99, description="2-digit province code", examples=[33])]
Kabupaten = Annotated[int, Path(ge=1, le=99, description="Regency or city number within the province, 1-99", examples=[1])]
Kecamatan = Annotated[int, Path(ge=1, le=99, description="District number within the regency, 1-99", examples=[1])]
Desa = Annotated[int, Path(ge=1, le=9999, description="Village number within the district, 1-9999", examples=[2001])]


@router.get(
    "/{kode_provinsi}",
    summary="Shorthand: province",
    response_model=SuccessResponse[RegionResource],
)
def simple_provinsi(request: Request, kode_provinsi: Provinsi, service: Service, parent: ChainParent = True) -> object:
    return success_response(request, service.resolve_short([kode_provinsi], include_parent=parent))


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}",
    summary="Shorthand: regency or city",
    response_model=SuccessResponse[RegionResource],
)
def simple_kabupaten(
    request: Request,
    kode_provinsi: Provinsi,
    nomor_kabupaten: Kabupaten,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [kode_provinsi, nomor_kabupaten]
    return success_response(request, service.resolve_short(segments, include_parent=parent))


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}",
    summary="Shorthand: district",
    response_model=SuccessResponse[RegionResource],
)
def simple_kecamatan(
    request: Request,
    kode_provinsi: Provinsi,
    nomor_kabupaten: Kabupaten,
    nomor_kecamatan: Kecamatan,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [kode_provinsi, nomor_kabupaten, nomor_kecamatan]
    return success_response(request, service.resolve_short(segments, include_parent=parent))


@router.get(
    "/{kode_provinsi}/{nomor_kabupaten}/{nomor_kecamatan}/{nomor_desa}",
    summary="Shorthand: village",
    response_model=SuccessResponse[RegionResource],
)
def simple_desa(
    request: Request,
    kode_provinsi: Provinsi,
    nomor_kabupaten: Kabupaten,
    nomor_kecamatan: Kecamatan,
    nomor_desa: Desa,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [kode_provinsi, nomor_kabupaten, nomor_kecamatan, nomor_desa]
    return success_response(request, service.resolve_short(segments, include_parent=parent))

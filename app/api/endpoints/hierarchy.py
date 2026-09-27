"""Hierarchy listings by full codes: /api/0 lists provinces, each extra segment goes one level down."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import ItemParent, Service
from app.api.examples import LIST_EXAMPLE, responses
from app.core.responses import list_response
from app.schemas.common import SuccessResponse
from app.schemas.regions import RegionListData

router = APIRouter(
    tags=["hierarchy"],
    responses=responses(LIST_EXAMPLE),
)

Province = Annotated[int, Path(gt=0, description="2-digit province code", examples=[33])]
Regency = Annotated[int, Path(gt=0, description="4-digit regency or city code", examples=[3301])]
District = Annotated[int, Path(gt=0, description="6-digit district code", examples=[330101])]


@router.get(
    "/0",
    summary="List provinces",
    description="Every province in Indonesia.",
    response_model=SuccessResponse[RegionListData],
)
def list_provinces(request: Request, service: Service) -> object:
    return list_response(request, service.list_children([], include_parent=False))


@router.get(
    "/{province_code}",
    summary="List regencies and cities",
    description="Regencies and cities in a province.",
    response_model=SuccessResponse[RegionListData],
)
def list_regencies(request: Request, province_code: Province, service: Service, parent: ItemParent = False) -> object:
    return list_response(request, service.list_children([province_code], include_parent=parent))


@router.get(
    "/{province_code}/{regency_code}",
    summary="List districts",
    description="Districts in a regency or city.",
    response_model=SuccessResponse[RegionListData],
)
def list_districts(
    request: Request,
    province_code: Province,
    regency_code: Regency,
    service: Service,
    parent: ItemParent = False,
) -> object:
    codes = [province_code, regency_code]
    return list_response(request, service.list_children(codes, include_parent=parent))


@router.get(
    "/{province_code}/{regency_code}/{district_code}",
    summary="List villages",
    description="Villages in a district.",
    response_model=SuccessResponse[RegionListData],
)
def list_villages(
    request: Request,
    province_code: Province,
    regency_code: Regency,
    district_code: District,
    service: Service,
    parent: ItemParent = False,
) -> object:
    codes = [province_code, regency_code, district_code]
    return list_response(request, service.list_children(codes, include_parent=parent))

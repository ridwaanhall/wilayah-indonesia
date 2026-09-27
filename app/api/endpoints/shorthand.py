"""Shorthand lookups by segment: /api/s/33/1/1/2001 resolves to village 3301012001."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import ChainParent, Service
from app.api.examples import REGION_EXAMPLE, responses
from app.core.responses import success_response
from app.schemas.common import SuccessResponse
from app.schemas.regions import RegionResource

router = APIRouter(
    prefix="/s",
    tags=["shorthand"],
    responses=responses(REGION_EXAMPLE),
)

Province = Annotated[int, Path(ge=1, le=99, description="2-digit province code", examples=[33])]
Regency = Annotated[int, Path(ge=1, le=99, description="Regency or city number in the province, 1-99", examples=[1])]
District = Annotated[int, Path(ge=1, le=99, description="District number in the regency, 1-99", examples=[1])]
Village = Annotated[int, Path(ge=1, le=9999, description="Village number in the district, 1-9999", examples=[2001])]


@router.get(
    "/{province_code}",
    summary="Shorthand: province",
    response_model=SuccessResponse[RegionResource],
)
def shorthand_province(request: Request, province_code: Province, service: Service, parent: ChainParent = True) -> object:
    return success_response(request, service.resolve_short([province_code], include_parent=parent))


@router.get(
    "/{province_code}/{regency_number}",
    summary="Shorthand: regency or city",
    response_model=SuccessResponse[RegionResource],
)
def shorthand_regency(
    request: Request,
    province_code: Province,
    regency_number: Regency,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [province_code, regency_number]
    return success_response(request, service.resolve_short(segments, include_parent=parent))


@router.get(
    "/{province_code}/{regency_number}/{district_number}",
    summary="Shorthand: district",
    response_model=SuccessResponse[RegionResource],
)
def shorthand_district(
    request: Request,
    province_code: Province,
    regency_number: Regency,
    district_number: District,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [province_code, regency_number, district_number]
    return success_response(request, service.resolve_short(segments, include_parent=parent))


@router.get(
    "/{province_code}/{regency_number}/{district_number}/{village_number}",
    summary="Shorthand: village",
    response_model=SuccessResponse[RegionResource],
)
def shorthand_village(
    request: Request,
    province_code: Province,
    regency_number: Regency,
    district_number: District,
    village_number: Village,
    service: Service,
    parent: ChainParent = True,
) -> object:
    segments = [province_code, regency_number, district_number, village_number]
    return success_response(request, service.resolve_short(segments, include_parent=parent))

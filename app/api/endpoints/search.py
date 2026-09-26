"""Direct lookup of any region by its full code."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import ChainParent, Service
from app.api.examples import REGION_EXAMPLE, responses
from app.core.responses import success_response
from app.schemas.common import SuccessResponse
from app.schemas.wilayah import RegionResource

router = APIRouter(tags=["search"])


@router.get(
    "/kode/{kode}",
    summary="Cari Wilayah berdasarkan Kode",
    description="Cari wilayah pada level apa pun dengan kode penuh 2, 4, 6, atau 10 digit.",
    response_model=SuccessResponse[RegionResource],
    responses=responses(REGION_EXAMPLE),
)
def search_by_code(
    request: Request,
    kode: Annotated[int, Path(gt=0, description="Kode wilayah administratif", examples=[3301012001])],
    service: Service,
    parent: ChainParent = True,
) -> object:
    return success_response(request, service.search_by_code(kode, include_parent=parent))

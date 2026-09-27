"""Precomputed descendant totals for analytics."""

from typing import Annotated

from fastapi import APIRouter, Path, Request

from app.api.deps import Service
from app.api.examples import STATS_EXAMPLE, responses
from app.core.responses import success_response
from app.schemas.common import SuccessResponse
from app.schemas.wilayah import StatsData

router = APIRouter(tags=["stats"])


@router.get(
    "/stats/{kode}",
    summary="Region statistics",
    description=(
        "Descendant counts per level (levels) and per kind (kinds: kabupaten/kota, "
        "desa/kelurahan/desa adat) for one region and each of its direct children. "
        "Use code 0 for the whole of Indonesia."
    ),
    response_model=SuccessResponse[StatsData],
    responses=responses(STATS_EXAMPLE),
)
def region_stats(
    request: Request,
    kode: Annotated[int, Path(ge=0, description="Full region code, or 0 for Indonesia", examples=[33])],
    service: Service,
) -> object:
    return success_response(request, service.stats(kode))

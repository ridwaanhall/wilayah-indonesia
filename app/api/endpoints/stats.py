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
    summary="Statistik Wilayah",
    description=(
        "Jumlah wilayah turunan per level (levels) dan per jenis (kinds: kabupaten/kota, "
        "desa/kelurahan/desa adat) untuk satu wilayah beserta setiap anak langsungnya. "
        "Gunakan kode 0 untuk seluruh Indonesia."
    ),
    response_model=SuccessResponse[StatsData],
    responses=responses(STATS_EXAMPLE),
)
def region_stats(
    request: Request,
    kode: Annotated[int, Path(ge=0, description="Kode wilayah, atau 0 untuk Indonesia", examples=[33])],
    service: Service,
) -> object:
    return success_response(request, service.stats(kode))

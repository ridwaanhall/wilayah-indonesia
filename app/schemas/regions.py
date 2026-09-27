from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginationInfo

RegionType = Literal["province", "regency", "district", "village"]


class RegionParent(BaseModel):
    """Recursive parent chain object for region resources."""

    model_config = ConfigDict(frozen=True)

    code: int
    short_code: str
    name: str
    depth: int = Field(ge=1, le=4)
    type: RegionType
    parent: "RegionParent | None" = None


class RegionResource(BaseModel):
    """Canonical region resource returned by all data endpoints."""

    model_config = ConfigDict(frozen=True)

    code: int
    short_code: str
    name: str
    depth: int = Field(ge=1, le=4)
    type: RegionType
    has_children: bool
    parent: RegionParent | None = None


class RegionListData(BaseModel):
    """Typed list payload for region collection responses."""

    items: list[RegionResource]
    pagination: PaginationInfo


class LevelCounts(BaseModel):
    """Number of descendant regions at each level."""

    province: int = Field(ge=0)
    regency: int = Field(ge=0)
    district: int = Field(ge=0)
    village: int = Field(ge=0)


class KindCounts(BaseModel):
    """Descendant regency-level regions split into regencies and cities, villages by status.

    regency + city equals levels.regency; the three village kinds sum to levels.village.
    """

    regency: int = Field(ge=0, description="Kabupaten")
    city: int = Field(ge=0, description="Kota")
    rural_village: int = Field(ge=0, description="Desa")
    urban_village: int = Field(ge=0, description="Kelurahan")
    customary_village: int = Field(ge=0, description="Desa adat")


class RegionStats(BaseModel):
    """Descendant totals for one region."""

    region: RegionResource
    levels: LevelCounts
    kinds: KindCounts


class StatsData(BaseModel):
    """Totals for a region (null region = Indonesia) and for each direct child."""

    region: RegionResource | None
    levels: LevelCounts
    kinds: KindCounts
    children: list[RegionStats]


RegionParent.model_rebuild()

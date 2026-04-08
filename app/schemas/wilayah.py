from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

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


RegionParent.model_rebuild()

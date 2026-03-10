from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class ParentInfo(BaseModel):
    """Parent region information."""

    model_config = ConfigDict(frozen=True)

    kode: int
    nama: str
    tingkat: int


class WilayahBase(BaseModel):
    """Base schema for all administrative region levels."""

    model_config = ConfigDict(frozen=True)

    kode: int
    nama: str
    tingkat: int


class Provinsi(WilayahBase):
    """Province - administrative level 1."""


class Kabupaten(WilayahBase):
    """Regency / city - administrative level 2."""

    parent: Optional[ParentInfo] = Field(None, description="Parent provinsi information")


class Kecamatan(WilayahBase):
    """District - administrative level 3."""

    parent: Optional[ParentInfo] = Field(None, description="Parent kabupaten information")


class Desa(WilayahBase):
    """Village / sub-district - administrative level 4."""

    parent: Optional[ParentInfo] = Field(None, description="Parent kecamatan information")


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str

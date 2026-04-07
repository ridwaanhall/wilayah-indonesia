from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


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
    """Province schema (tingkat 1)."""


class Kabupaten(WilayahBase):
    """Regency/city schema (tingkat 2)."""

    parent: ParentInfo | None = Field(default=None)


class Kecamatan(WilayahBase):
    """District schema (tingkat 3)."""

    parent: ParentInfo | None = Field(default=None)


class Desa(WilayahBase):
    """Village schema (tingkat 4)."""

    parent: ParentInfo | None = Field(default=None)


SimpleLevel: TypeAlias = Literal["provinsi", "kabupaten", "kecamatan"]


class SimpleWilayahData(BaseModel):
    """Response body for simple code resolution."""

    kode_lengkap: int = Field(description="Canonical wilayah code as integer")
    kode_singkat: str = Field(description="Simple shorthand code")
    kode: int = Field(description="Canonical wilayah code as integer")
    nama: str
    tingkat: int = Field(description="Administrative level (1=provinsi, 2=kabupaten, 3=kecamatan)")
    level: SimpleLevel
    parent: ParentInfo | None = None


class SimpleWilayahResponse(BaseModel):
    """Standard success response for the simple endpoints."""

    success: Literal[True] = True
    message: str
    data: SimpleWilayahData

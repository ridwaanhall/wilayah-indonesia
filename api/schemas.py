from pydantic import BaseModel, ConfigDict


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

    provinsi: int


class Kecamatan(WilayahBase):
    """District - administrative level 3."""

    kabupaten: int


class Desa(WilayahBase):
    """Village / sub-district - administrative level 4."""

    kecamatan: int


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str

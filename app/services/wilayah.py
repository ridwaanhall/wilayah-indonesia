"""Service layer for wilayah lookups and hierarchical validation."""

from typing import Any

from fastapi import HTTPException, status

from app.services.data_loader import DataLoader


class WilayahService:
    """Encapsulates wilayah query rules to keep endpoint handlers minimal and DRY."""

    def __init__(self, loader: DataLoader) -> None:
        self.loader = loader

    @staticmethod
    def _ensure_code_length(name: str, code: int, length: int) -> None:
        """Validate numeric code length for hierarchical endpoints."""
        if len(str(code)) != length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Parameter {name} harus terdiri dari {length} digit angka.",
            )

    @staticmethod
    def _not_found_detail(entity: str) -> str:
        """Create professional and consistent not-found messages."""
        return (
            f"Data {entity} yang diminta tidak ditemukan. "
            "Pastikan kode wilayah benar dan tersedia pada dataset resmi."
        )

    def list_provinsi(self) -> list[dict[str, Any]]:
        """Return all provinces."""
        return self.loader.provinsi_list

    def search_by_code(self, kode: int) -> dict[str, Any]:
        """Return wilayah by code across all administrative levels."""
        result = self.loader.find_by_code(kode)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("wilayah"),
            )
        return result

    def list_kabupaten(self, kode_provinsi: int, include_parent: bool) -> list[dict[str, Any]]:
        """Return kabupaten list for a province."""
        self._ensure_code_length("kode_provinsi", kode_provinsi, 2)
        result = self.loader.kabupaten_by_provinsi(kode_provinsi, include_parent=include_parent)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )
        return result

    def list_kecamatan(
        self,
        kode_provinsi: int,
        kode_kabupaten: int,
        include_parent: bool,
    ) -> list[dict[str, Any]]:
        """Return kecamatan list for a kabupaten in a province."""
        self._ensure_code_length("kode_provinsi", kode_provinsi, 2)
        self._ensure_code_length("kode_kabupaten", kode_kabupaten, 4)

        if not self.loader.provinsi_exists(kode_provinsi):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kabupaten/kota"),
            )

        return self.loader.kecamatan_by_kabupaten(
            kode_kabupaten,
            kode_provinsi=kode_provinsi,
            include_parent=include_parent,
        ) or []

    def list_desa(
        self,
        kode_provinsi: int,
        kode_kabupaten: int,
        kode_kecamatan: int,
        include_parent: bool,
    ) -> list[dict[str, Any]]:
        """Return desa list for a kecamatan in a kabupaten and province."""
        self._ensure_code_length("kode_provinsi", kode_provinsi, 2)
        self._ensure_code_length("kode_kabupaten", kode_kabupaten, 4)
        self._ensure_code_length("kode_kecamatan", kode_kecamatan, 6)

        if not self.loader.provinsi_exists(kode_provinsi):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kabupaten/kota"),
            )
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan, kode_kabupaten):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kecamatan"),
            )

        return self.loader.desa_by_kecamatan(
            kode_kecamatan,
            kode_kabupaten=kode_kabupaten,
            include_parent=include_parent,
        ) or []

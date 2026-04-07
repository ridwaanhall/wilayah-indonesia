"""Service layer for simplified wilayah code resolution."""

from typing import Any

from fastapi import HTTPException, status

from app.schemas.wilayah import SimpleLevel, SimpleWilayahData, SimpleWilayahResponse
from app.services.data_loader import DataLoader


class SimpleWilayahService:
    """Resolve simple shorthand codes to canonical wilayah objects."""

    def __init__(self, loader: DataLoader) -> None:
        """Initialize service with data loader dependency."""
        self.loader = loader

    @staticmethod
    def _format_two_digit_segment(name: str, value: int) -> str:
        """Validate and return a two-digit segment string."""
        if value < 1 or value > 99:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Parameter {name} harus berada pada rentang 1 hingga 99.",
            )
        return f"{value:02d}"

    @staticmethod
    def _level_label(tingkat: int) -> SimpleLevel:
        """Return typed label for simple endpoint levels."""
        if tingkat == 1:
            return "provinsi"
        if tingkat == 2:
            return "kabupaten"
        if tingkat == 3:
            return "kecamatan"
        raise ValueError("Unsupported tingkat for simple endpoint")

    def _build_data(
        self,
        item: dict[str, Any],
        kode_singkat: str,
        kode_lengkap: int,
    ) -> SimpleWilayahData:
        """Build standardized simple response payload."""
        return SimpleWilayahData(
            kode_lengkap=kode_lengkap,
            kode_singkat=kode_singkat,
            kode=item["kode"],
            nama=item["nama"],
            tingkat=item["tingkat"],
            level=self._level_label(item["tingkat"]),
            parent=item.get("parent"),
        )

    @staticmethod
    def _not_found_detail(entity: str) -> str:
        """Create professional and consistent not-found messages."""
        return (
            f"Data {entity} yang diminta tidak ditemukan. "
            "Pastikan kode wilayah benar dan tersedia pada dataset resmi."
        )

    def get_provinsi(self, kode_provinsi: int) -> SimpleWilayahResponse:
        """Resolve a province using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kode = int(provinsi_segment)
        item = self.loader.find_by_code(kode)
        if item is None or item["tingkat"] != 1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )

        return SimpleWilayahResponse(
            message="Data provinsi berhasil ditemukan.",
            data=self._build_data(item, kode_singkat=provinsi_segment, kode_lengkap=kode),
        )

    def get_kabupaten(self, kode_provinsi: int, nomor_kabupaten: int) -> SimpleWilayahResponse:
        """Resolve a kabupaten/kota using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kabupaten_segment = self._format_two_digit_segment("nomor_kabupaten", nomor_kabupaten)

        if not self.loader.provinsi_exists(int(provinsi_segment)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )

        kode_lengkap = f"{provinsi_segment}{kabupaten_segment}"
        kode = int(kode_lengkap)
        if not self.loader.kabupaten_in_provinsi(kode, int(provinsi_segment)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kabupaten/kota"),
            )

        item = self.loader.find_by_code(kode)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kabupaten/kota"),
            )

        return SimpleWilayahResponse(
            message="Data kabupaten/kota berhasil ditemukan.",
            data=self._build_data(
                item,
                kode_singkat=f"{provinsi_segment}/{kabupaten_segment}",
                kode_lengkap=kode,
            ),
        )

    def get_kecamatan(
        self,
        kode_provinsi: int,
        nomor_kabupaten: int,
        nomor_kecamatan: int,
    ) -> SimpleWilayahResponse:
        """Resolve a kecamatan using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kabupaten_segment = self._format_two_digit_segment("nomor_kabupaten", nomor_kabupaten)
        kecamatan_segment = self._format_two_digit_segment("nomor_kecamatan", nomor_kecamatan)

        kode_provinsi_int = int(provinsi_segment)
        kode_kabupaten_int = int(f"{provinsi_segment}{kabupaten_segment}")
        kode_kecamatan_lengkap = f"{provinsi_segment}{kabupaten_segment}{kecamatan_segment}"
        kode_kecamatan_int = int(kode_kecamatan_lengkap)

        if not self.loader.provinsi_exists(kode_provinsi_int):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("provinsi"),
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kabupaten/kota"),
            )
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan_int, kode_kabupaten_int):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kecamatan"),
            )

        item = self.loader.find_by_code(kode_kecamatan_int)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=self._not_found_detail("kecamatan"),
            )

        return SimpleWilayahResponse(
            message="Data kecamatan berhasil ditemukan.",
            data=self._build_data(
                item,
                kode_singkat=f"{provinsi_segment}/{kabupaten_segment}/{kecamatan_segment}",
                kode_lengkap=kode_kecamatan_int,
            ),
        )

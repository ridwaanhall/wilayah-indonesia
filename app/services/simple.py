from typing import Any

from fastapi import HTTPException

from app.schemas.wilayah import SimpleWilayahData, SimpleWilayahResponse
from app.services.data_loader import DataLoader


class SimpleWilayahService:
    """Resolve simple shorthand codes to canonical wilayah objects."""

    def __init__(self, loader: DataLoader) -> None:
        self.loader = loader

    @staticmethod
    def _validate_segment(name: str, value: str, digits: int) -> str:
        if not value.isdigit() or len(value) != digits:
            raise HTTPException(
                status_code=422,
                detail=f"{name} harus berupa {digits} digit angka.",
            )
        return value

    @staticmethod
    def _level_label(tingkat: int) -> str:
        labels = {
            1: "provinsi",
            2: "kabupaten",
            3: "kecamatan",
        }
        return labels.get(tingkat, "wilayah")

    def _build_data(
        self,
        item: dict[str, Any],
        kode_singkat: str,
        kode_lengkap: str,
    ) -> SimpleWilayahData:
        return SimpleWilayahData(
            kode_lengkap=kode_lengkap,
            kode_singkat=kode_singkat,
            kode=item["kode"],
            nama=item["nama"],
            tingkat=item["tingkat"],
            level=self._level_label(item["tingkat"]),
            parent=item.get("parent"),
        )

    def get_provinsi(self, kode_provinsi: str) -> SimpleWilayahResponse:
        provinsi_segment = self._validate_segment("kode_provinsi", kode_provinsi, 2)
        kode = int(provinsi_segment)
        item = self.loader.find_by_code(kode)
        if item is None or item["tingkat"] != 1:
            raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")

        return SimpleWilayahResponse(
            message="Data provinsi berhasil ditemukan.",
            data=self._build_data(item, kode_singkat=provinsi_segment, kode_lengkap=provinsi_segment),
        )

    def get_kabupaten(self, kode_provinsi: str, nomor_kabupaten: str) -> SimpleWilayahResponse:
        provinsi_segment = self._validate_segment("kode_provinsi", kode_provinsi, 2)
        kabupaten_segment = self._validate_segment("nomor_kabupaten", nomor_kabupaten, 2)

        if not self.loader.provinsi_exists(int(provinsi_segment)):
            raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")

        kode_lengkap = f"{provinsi_segment}{kabupaten_segment}"
        kode = int(kode_lengkap)
        if not self.loader.kabupaten_in_provinsi(kode, int(provinsi_segment)):
            raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")

        item = self.loader.find_by_code(kode)
        if item is None:
            raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")

        return SimpleWilayahResponse(
            message="Data kabupaten/kota berhasil ditemukan.",
            data=self._build_data(
                item,
                kode_singkat=f"{provinsi_segment}/{kabupaten_segment}",
                kode_lengkap=kode_lengkap,
            ),
        )

    def get_kecamatan(
        self,
        kode_provinsi: str,
        nomor_kabupaten: str,
        nomor_kecamatan: str,
    ) -> SimpleWilayahResponse:
        provinsi_segment = self._validate_segment("kode_provinsi", kode_provinsi, 2)
        kabupaten_segment = self._validate_segment("nomor_kabupaten", nomor_kabupaten, 2)
        kecamatan_segment = self._validate_segment("nomor_kecamatan", nomor_kecamatan, 2)

        kode_provinsi_int = int(provinsi_segment)
        kode_kabupaten_int = int(f"{provinsi_segment}{kabupaten_segment}")
        kode_kecamatan_lengkap = f"{provinsi_segment}{kabupaten_segment}{kecamatan_segment}"
        kode_kecamatan_int = int(kode_kecamatan_lengkap)

        if not self.loader.provinsi_exists(kode_provinsi_int):
            raise HTTPException(status_code=404, detail="Provinsi tidak ditemukan.")
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
            raise HTTPException(status_code=404, detail="Kabupaten/Kota tidak ditemukan.")
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan_int, kode_kabupaten_int):
            raise HTTPException(status_code=404, detail="Kecamatan tidak ditemukan.")

        item = self.loader.find_by_code(kode_kecamatan_int)
        if item is None:
            raise HTTPException(status_code=404, detail="Kecamatan tidak ditemukan.")

        return SimpleWilayahResponse(
            message="Data kecamatan berhasil ditemukan.",
            data=self._build_data(
                item,
                kode_singkat=f"{provinsi_segment}/{kabupaten_segment}/{kecamatan_segment}",
                kode_lengkap=kode_kecamatan_lengkap,
            ),
        )

"""Service layer for simplified wilayah code resolution."""

from fastapi import status

from app.core.errors import ApiException
from app.services.data_loader import DataLoader
from app.services.wilayah import WilayahService


class SimpleWilayahService:
    """Resolve simple shorthand codes to canonical wilayah objects."""

    def __init__(self, loader: DataLoader) -> None:
        """Initialize service with data loader dependency."""
        self.loader = loader
        self.wilayah_service = WilayahService(loader)

    @staticmethod
    def _format_two_digit_segment(name: str, value: int) -> str:
        """Validate and return a two-digit segment string."""
        if value < 1 or value > 99:
            raise ApiException(
                status_code=422,
                code="INVALID_REGION_CODE",
                message="The region code format is invalid.",
                detail=f"Parameter {name} must be an integer between 1 and 99.",
                hint=f"Provide {name} as a positive 2-digit segment.",
                fields=[
                    {
                        "field": name,
                        "value": value,
                        "rule": "range:1-99",
                        "message": f"{name} must be between 1 and 99.",
                    }
                ],
            )
        return f"{value:02d}"

    @staticmethod
    def _format_four_digit_segment(name: str, value: int) -> str:
        """Validate and return a four-digit segment string."""
        if value < 1 or value > 9999:
            raise ApiException(
                status_code=422,
                code="INVALID_REGION_CODE",
                message="The region code format is invalid.",
                detail=f"Parameter {name} must be an integer between 1 and 9999.",
                hint=f"Provide {name} as a positive 4-digit segment.",
                fields=[
                    {
                        "field": name,
                        "value": value,
                        "rule": "range:1-9999",
                        "message": f"{name} must be between 1 and 9999.",
                    }
                ],
            )
        return f"{value:04d}"

    @staticmethod
    def _raise_not_found(entity: str, detail: str) -> None:
        mapping = {
            "province": {
                "code": "PROVINCE_NOT_FOUND",
                "message": "The requested province could not be found.",
                "hint": "Verify the province code with GET /api/0.",
            },
            "regency": {
                "code": "REGENCY_NOT_FOUND",
                "message": "The requested regency could not be found.",
                "hint": "Check that the regency segment belongs to the provided province.",
            },
            "district": {
                "code": "DISTRICT_NOT_FOUND",
                "message": "The requested district could not be found.",
                "hint": "Check that the district segment belongs to the provided regency.",
            },
            "village": {
                "code": "VILLAGE_NOT_FOUND",
                "message": "The requested village could not be found.",
                "hint": "Check that the village segment belongs to the provided district.",
            },
        }
        item = mapping[entity]
        raise ApiException(
            status_code=status.HTTP_404_NOT_FOUND,
            code=item["code"],
            message=item["message"],
            detail=detail,
            hint=item["hint"],
            fields=None,
        )

    def get_provinsi(self, kode_provinsi: int, *, include_parent: bool = True) -> dict[str, object]:
        """Resolve a province using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kode = int(provinsi_segment)
        if not self.loader.provinsi_exists(kode):
            self._raise_not_found(
                "province",
                detail=f"No province with code {kode} exists in the national reference dataset.",
            )
        return self.wilayah_service.search_by_code(kode, include_parent=include_parent)

    def get_kabupaten(
        self,
        kode_provinsi: int,
        nomor_kabupaten: int,
        *,
        include_parent: bool = True,
    ) -> dict[str, object]:
        """Resolve a kabupaten/kota using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kabupaten_segment = self._format_two_digit_segment("nomor_kabupaten", nomor_kabupaten)

        if not self.loader.provinsi_exists(int(provinsi_segment)):
            self._raise_not_found(
                "province",
                detail=(
                    f"No province with code {int(provinsi_segment)} exists "
                    "in the national reference dataset."
                ),
            )

        kode = int(f"{provinsi_segment}{kabupaten_segment}")
        if not self.loader.kabupaten_in_provinsi(kode, int(provinsi_segment)):
            self._raise_not_found(
                "regency",
                detail=(
                    f"No regency with code {kode} exists under province "
                    f"{int(provinsi_segment)} in the national reference dataset."
                ),
            )

        return self.wilayah_service.search_by_code(kode, include_parent=include_parent)

    def get_kecamatan(
        self,
        kode_provinsi: int,
        nomor_kabupaten: int,
        nomor_kecamatan: int,
        *,
        include_parent: bool = True,
    ) -> dict[str, object]:
        """Resolve a kecamatan using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kabupaten_segment = self._format_two_digit_segment("nomor_kabupaten", nomor_kabupaten)
        kecamatan_segment = self._format_two_digit_segment("nomor_kecamatan", nomor_kecamatan)

        kode_provinsi_int = int(provinsi_segment)
        kode_kabupaten_int = int(f"{provinsi_segment}{kabupaten_segment}")
        kode_kecamatan_lengkap = f"{provinsi_segment}{kabupaten_segment}{kecamatan_segment}"
        kode_kecamatan_int = int(kode_kecamatan_lengkap)

        if not self.loader.provinsi_exists(kode_provinsi_int):
            self._raise_not_found(
                "province",
                detail=(
                    f"No province with code {kode_provinsi_int} exists "
                    "in the national reference dataset."
                ),
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
            self._raise_not_found(
                "regency",
                detail=(
                    f"No regency with code {kode_kabupaten_int} exists under province "
                    f"{kode_provinsi_int} in the national reference dataset."
                ),
            )
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan_int, kode_kabupaten_int):
            self._raise_not_found(
                "district",
                detail=(
                    f"No district with code {kode_kecamatan_int} exists under regency "
                    f"{kode_kabupaten_int} in the national reference dataset."
                ),
            )

        return self.wilayah_service.search_by_code(
            kode_kecamatan_int,
            include_parent=include_parent,
        )

    def get_desa(
        self,
        kode_provinsi: int,
        nomor_kabupaten: int,
        nomor_kecamatan: int,
        nomor_desa: int,
        *,
        include_parent: bool = True,
    ) -> dict[str, object]:
        """Resolve a desa/kelurahan using simplified code format."""
        provinsi_segment = self._format_two_digit_segment("kode_provinsi", kode_provinsi)
        kabupaten_segment = self._format_two_digit_segment("nomor_kabupaten", nomor_kabupaten)
        kecamatan_segment = self._format_two_digit_segment("nomor_kecamatan", nomor_kecamatan)
        desa_segment = self._format_four_digit_segment("nomor_desa", nomor_desa)

        kode_provinsi_int = int(provinsi_segment)
        kode_kabupaten_int = int(f"{provinsi_segment}{kabupaten_segment}")
        kode_kecamatan_int = int(f"{provinsi_segment}{kabupaten_segment}{kecamatan_segment}")
        kode_desa_int = int(f"{provinsi_segment}{kabupaten_segment}{kecamatan_segment}{desa_segment}")

        if not self.loader.provinsi_exists(kode_provinsi_int):
            self._raise_not_found(
                "province",
                detail=(
                    f"No province with code {kode_provinsi_int} exists "
                    "in the national reference dataset."
                ),
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten_int, kode_provinsi_int):
            self._raise_not_found(
                "regency",
                detail=(
                    f"No regency with code {kode_kabupaten_int} exists under province "
                    f"{kode_provinsi_int} in the national reference dataset."
                ),
            )
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan_int, kode_kabupaten_int):
            self._raise_not_found(
                "district",
                detail=(
                    f"No district with code {kode_kecamatan_int} exists under regency "
                    f"{kode_kabupaten_int} in the national reference dataset."
                ),
            )
        if not self.loader.desa_in_kecamatan(kode_desa_int, kode_kecamatan_int):
            self._raise_not_found(
                "village",
                detail=(
                    f"No village with code {kode_desa_int} exists under district "
                    f"{kode_kecamatan_int} in the national reference dataset."
                ),
            )

        return self.wilayah_service.search_by_code(
            kode_desa_int,
            include_parent=include_parent,
        )

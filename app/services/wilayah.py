"""Service layer for wilayah lookups and hierarchical validation."""

from typing import Any

from fastapi import status

from app.core.errors import ApiException
from app.services.data_loader import DataLoader


DEPTH_TO_TYPE: dict[int, str] = {
    1: "province",
    2: "regency",
    3: "district",
    4: "village",
}

DEPTH_TO_LENGTH: dict[int, int] = {
    1: 2,
    2: 4,
    3: 6,
    4: 10,
}


class WilayahService:
    """Encapsulates wilayah query rules to keep endpoint handlers minimal and DRY."""

    def __init__(self, loader: DataLoader) -> None:
        self.loader = loader

    @staticmethod
    def _ensure_code_length(name: str, code: int, length: int) -> None:
        """Validate numeric code length for hierarchical endpoints."""
        if len(str(code)) != length:
            raise ApiException(
                status_code=422,
                code="INVALID_REGION_CODE",
                message="The region code format is invalid.",
                detail=f"Parameter {name} must be a {length}-digit numeric code. Received: {code}.",
                hint=f"Provide {name} as exactly {length} digits.",
                fields=[
                    {
                        "field": name,
                        "value": code,
                        "rule": f"digits:{length}",
                        "message": f"{name} must contain exactly {length} digits.",
                    }
                ],
            )

    @staticmethod
    def _short_code(code: int, depth: int) -> str:
        code_length = DEPTH_TO_LENGTH[depth]
        code_text = f"{code:0{code_length}d}"
        if depth == 1:
            return code_text[0:2]
        if depth == 2:
            return f"{code_text[0:2]}/{code_text[2:4]}"
        if depth == 3:
            return f"{code_text[0:2]}/{code_text[2:4]}/{code_text[4:6]}"
        return f"{code_text[0:2]}/{code_text[2:4]}/{code_text[4:6]}/{code_text[6:10]}"

    @staticmethod
    def _raise_not_found(entity: str, detail: str) -> None:
        mapping = {
            "region": {
                "code": "REGION_NOT_FOUND",
                "message": "The requested region could not be found.",
                "hint": "Verify the region code using GET /api/0 for valid province codes.",
            },
            "province": {
                "code": "PROVINCE_NOT_FOUND",
                "message": "The requested province could not be found.",
                "hint": "Verify the province code with GET /api/0.",
            },
            "regency": {
                "code": "REGENCY_NOT_FOUND",
                "message": "The requested regency could not be found.",
                "hint": "Check that the regency code belongs to the provided province.",
            },
            "district": {
                "code": "DISTRICT_NOT_FOUND",
                "message": "The requested district could not be found.",
                "hint": "Check that the district code belongs to the provided regency.",
            },
            "village": {
                "code": "VILLAGE_NOT_FOUND",
                "message": "The requested village could not be found.",
                "hint": "Check that the village code belongs to the provided district.",
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

    @staticmethod
    def _ensure_search_code_length(kode: int) -> None:
        if len(str(kode)) not in {2, 4, 6, 10}:
            raise ApiException(
                status_code=422,
                code="INVALID_REGION_CODE",
                message="The region code format is invalid.",
                detail=(
                    "Parameter kode must use one of the supported code lengths: "
                    "2 (province), 4 (regency), 6 (district), or 10 (village)."
                ),
                hint="Provide a valid region code with 2, 4, 6, or 10 digits.",
                fields=[
                    {
                        "field": "kode",
                        "value": kode,
                        "rule": "digits:2|4|6|10",
                        "message": "kode must be 2, 4, 6, or 10 digits.",
                    }
                ],
            )

    def _build_parent(self, item: dict[str, Any], full_chain: bool) -> dict[str, Any] | None:
        parent_ref = item.get("parent")
        if parent_ref is None:
            return None

        parent_item = self.loader.find_by_code(parent_ref["kode"])
        if parent_item is None:
            return None

        return {
            "code": parent_item["kode"],
            "short_code": self._short_code(parent_item["kode"], parent_item["tingkat"]),
            "name": parent_item["nama"],
            "depth": parent_item["tingkat"],
            "type": DEPTH_TO_TYPE[parent_item["tingkat"]],
            "parent": self._build_parent(parent_item, full_chain=True) if full_chain else None,
        }

    def _build_region(
        self,
        item: dict[str, Any],
        *,
        include_parent: bool,
        full_chain: bool,
    ) -> dict[str, Any]:
        parent_payload: dict[str, Any] | None = None
        if item["tingkat"] > 1:
            if full_chain:
                parent_payload = self._build_parent(item, full_chain=True)
            elif include_parent:
                parent_payload = self._build_parent(item, full_chain=False)

        return {
            "code": item["kode"],
            "short_code": self._short_code(item["kode"], item["tingkat"]),
            "name": item["nama"],
            "depth": item["tingkat"],
            "type": DEPTH_TO_TYPE[item["tingkat"]],
            "has_children": self.loader.has_children(item["kode"], item["tingkat"]),
            "parent": parent_payload,
        }

    def list_provinsi(self) -> list[dict[str, Any]]:
        """Return all provinces."""
        return [
            self._build_region(item, include_parent=False, full_chain=False)
            for item in self.loader.provinsi_list
        ]

    def search_by_code(self, kode: int, *, include_parent: bool = True) -> dict[str, Any]:
        """Return wilayah by code across all administrative levels."""
        self._ensure_search_code_length(kode)
        result = self.loader.find_by_code(kode)
        if result is None:
            self._raise_not_found(
                "region",
                detail=f"No region with code {kode} exists in the national reference dataset.",
            )
        return self._build_region(
            result,
            include_parent=include_parent,
            full_chain=include_parent,
        )

    def list_kabupaten(self, kode_provinsi: int, include_parent: bool) -> list[dict[str, Any]]:
        """Return kabupaten list for a province."""
        self._ensure_code_length("kode_provinsi", kode_provinsi, 2)
        result = self.loader.kabupaten_by_provinsi(kode_provinsi, include_parent=True)
        if result is None:
            self._raise_not_found(
                "province",
                detail=f"No province with code {kode_provinsi} exists in the national reference dataset.",
            )
        return [
            self._build_region(item, include_parent=include_parent, full_chain=False)
            for item in result
        ]

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
            self._raise_not_found(
                "province",
                detail=f"No province with code {kode_provinsi} exists in the national reference dataset.",
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
            self._raise_not_found(
                "regency",
                detail=(
                    f"No regency with code {kode_kabupaten} exists under province "
                    f"{kode_provinsi} in the national reference dataset."
                ),
            )

        rows = self.loader.kecamatan_by_kabupaten(
            kode_kabupaten,
            kode_provinsi=kode_provinsi,
            include_parent=True,
        ) or []

        return [
            self._build_region(item, include_parent=include_parent, full_chain=False)
            for item in rows
        ]

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
            self._raise_not_found(
                "province",
                detail=f"No province with code {kode_provinsi} exists in the national reference dataset.",
            )
        if not self.loader.kabupaten_in_provinsi(kode_kabupaten, kode_provinsi):
            self._raise_not_found(
                "regency",
                detail=(
                    f"No regency with code {kode_kabupaten} exists under province "
                    f"{kode_provinsi} in the national reference dataset."
                ),
            )
        if not self.loader.kecamatan_in_kabupaten(kode_kecamatan, kode_kabupaten):
            self._raise_not_found(
                "district",
                detail=(
                    f"No district with code {kode_kecamatan} exists under regency "
                    f"{kode_kabupaten} in the national reference dataset."
                ),
            )

        rows = self.loader.desa_by_kecamatan(
            kode_kecamatan,
            kode_kabupaten=kode_kabupaten,
            include_parent=True,
        ) or []

        return [
            self._build_region(item, include_parent=include_parent, full_chain=False)
            for item in rows
        ]

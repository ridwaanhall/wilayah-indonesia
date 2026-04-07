import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"


class DataLoader:
    """Singleton that loads and indexes Indonesian administrative region data."""

    _instance: "DataLoader | None" = None

    def __new__(cls) -> "DataLoader":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_and_index()
        return cls._instance

    def _load_and_index(self) -> None:
        self._provinsi: list[dict[str, Any]] = self._read("provinsi.json")
        self._kabupaten: list[dict[str, Any]] = self._read("kabupaten.json")
        self._kecamatan: list[dict[str, Any]] = self._read("kecamatan.json")
        self._desa: list[dict[str, Any]] = self._read("desa.json")

        self._provinsi_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._provinsi
        }
        self._kabupaten_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._kabupaten
        }
        self._kecamatan_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._kecamatan
        }
        self._desa_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._desa
        }

        self._kabupaten_by_prov: dict[int, list[dict[str, Any]]] = {}
        for item in self._kabupaten:
            parent_kode = item["parent"]["kode"]
            self._kabupaten_by_prov.setdefault(parent_kode, []).append(item)

        self._kecamatan_by_kab: dict[int, list[dict[str, Any]]] = {}
        for item in self._kecamatan:
            parent_kode = item["parent"]["kode"]
            self._kecamatan_by_kab.setdefault(parent_kode, []).append(item)

        self._desa_by_kec: dict[int, list[dict[str, Any]]] = {}
        for item in self._desa:
            parent_kode = item["parent"]["kode"]
            self._desa_by_kec.setdefault(parent_kode, []).append(item)

        self._all_codes_idx: dict[int, dict[str, Any]] = {}
        self._all_codes_idx.update(self._provinsi_idx)
        self._all_codes_idx.update(self._kabupaten_idx)
        self._all_codes_idx.update(self._kecamatan_idx)
        self._all_codes_idx.update(self._desa_idx)

    @staticmethod
    def _read(filename: str) -> list[dict[str, Any]]:
        with open(DATA_DIR / filename, encoding="utf-8") as file_handle:
            return json.load(file_handle)

    @staticmethod
    def _remove_parent(item: dict[str, Any]) -> dict[str, Any]:
        result = dict(item)
        result.pop("parent", None)
        return result

    @staticmethod
    def _remove_parent_from_list(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [DataLoader._remove_parent(item) for item in items]

    @property
    def provinsi_list(self) -> list[dict[str, Any]]:
        return self._provinsi

    def provinsi_exists(self, kode: int) -> bool:
        return kode in self._provinsi_idx

    def kabupaten_exists(self, kode: int) -> bool:
        return kode in self._kabupaten_idx

    def kecamatan_exists(self, kode: int) -> bool:
        return kode in self._kecamatan_idx

    def kabupaten_in_provinsi(self, kode_kabupaten: int, kode_provinsi: int) -> bool:
        item = self._kabupaten_idx.get(kode_kabupaten)
        return item is not None and item["parent"]["kode"] == kode_provinsi

    def kecamatan_in_kabupaten(self, kode_kecamatan: int, kode_kabupaten: int) -> bool:
        item = self._kecamatan_idx.get(kode_kecamatan)
        return item is not None and item["parent"]["kode"] == kode_kabupaten

    def kabupaten_by_provinsi(
        self,
        kode_provinsi: int,
        include_parent: bool = False,
    ) -> list[dict[str, Any]] | None:
        if kode_provinsi not in self._provinsi_idx:
            return None
        result = self._kabupaten_by_prov.get(kode_provinsi, [])
        if include_parent:
            return result
        return self._remove_parent_from_list(result)

    def kecamatan_by_kabupaten(
        self,
        kode_kabupaten: int,
        kode_provinsi: int | None = None,
        include_parent: bool = False,
    ) -> list[dict[str, Any]] | None:
        kabupaten_item = self._kabupaten_idx.get(kode_kabupaten)
        if kabupaten_item is None:
            return None
        if kode_provinsi is not None and kabupaten_item["parent"]["kode"] != kode_provinsi:
            return None
        result = self._kecamatan_by_kab.get(kode_kabupaten, [])
        if include_parent:
            return result
        return self._remove_parent_from_list(result)

    def desa_by_kecamatan(
        self,
        kode_kecamatan: int,
        kode_kabupaten: int | None = None,
        include_parent: bool = False,
    ) -> list[dict[str, Any]] | None:
        kecamatan_item = self._kecamatan_idx.get(kode_kecamatan)
        if kecamatan_item is None:
            return None
        if kode_kabupaten is not None and kecamatan_item["parent"]["kode"] != kode_kabupaten:
            return None
        result = self._desa_by_kec.get(kode_kecamatan, [])
        if include_parent:
            return result
        return self._remove_parent_from_list(result)

    def find_by_code(self, kode: int) -> dict[str, Any] | None:
        return self._all_codes_idx.get(kode)


@lru_cache(maxsize=1)
def get_loader() -> DataLoader:
    return DataLoader()

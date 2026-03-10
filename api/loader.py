import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"


class DataLoader:
    """Singleton that loads and indexes Indonesian administrative region data.

    All JSON data is loaded once on first instantiation and indexed
    with ``dict`` look-ups for O(1) existence checks and O(1) list retrieval.
    """

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
        self._kabupaten_by_prov: dict[int, list[dict[str, Any]]] = {}
        for item in self._kabupaten:
            parent_kode = item["parent"]["kode"]
            self._kabupaten_by_prov.setdefault(parent_kode, []).append(item)

        self._kecamatan_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._kecamatan
        }
        self._kecamatan_by_kab: dict[int, list[dict[str, Any]]] = {}
        for item in self._kecamatan:
            parent_kode = item["parent"]["kode"]
            self._kecamatan_by_kab.setdefault(parent_kode, []).append(item)

        self._desa_idx: dict[int, dict[str, Any]] = {
            item["kode"]: item for item in self._desa
        }
        self._desa_by_kec: dict[int, list[dict[str, Any]]] = {}
        for item in self._desa:
            parent_kode = item["parent"]["kode"]
            self._desa_by_kec.setdefault(parent_kode, []).append(item)

        # Build comprehensive index for all codes across all levels
        self._all_codes_idx: dict[int, dict[str, Any]] = {}
        self._all_codes_idx.update(self._provinsi_idx)
        self._all_codes_idx.update(self._kabupaten_idx)
        self._all_codes_idx.update(self._kecamatan_idx)
        self._all_codes_idx.update(self._desa_idx)

    @staticmethod
    def _read(filename: str) -> list[dict[str, Any]]:
        with open(DATA_DIR / filename, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _remove_parent(item: dict[str, Any]) -> dict[str, Any]:
        """Remove parent field from item."""
        result = dict(item)
        result.pop("parent", None)
        return result

    @staticmethod
    def _remove_parent_from_list(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove parent field from list of items."""
        return [DataLoader._remove_parent(item) for item in items]

    @property
    def provinsi_list(self) -> list[dict[str, Any]]:
        """Return the full list of provinces."""
        return self._provinsi

    def kabupaten_by_provinsi(
        self, kode: int, include_parent: bool = False
    ) -> list[dict[str, Any]] | None:
        """Return regencies/cities for *kode* province, or ``None`` if unknown."""
        if kode not in self._provinsi_idx:
            return None
        result = self._kabupaten_by_prov.get(kode, [])
        if not include_parent and result:
            result = self._remove_parent_from_list(result)
        return result

    def kecamatan_by_kabupaten(
        self, kode: int, kode_provinsi: int | None = None, include_parent: bool = False
    ) -> list[dict[str, Any]] | None:
        """Return districts for *kode* regency, or ``None`` if unknown.

        If *kode_provinsi* is provided, also validates that *kode* belongs to
        that province; returns ``None`` when the hierarchy does not match.
        """
        item: dict[str, Any] | None = self._kabupaten_idx.get(kode)
        if item is None:
            return None
        if kode_provinsi is not None and item["parent"]["kode"] != kode_provinsi:
            return None
        result = self._kecamatan_by_kab.get(kode, [])
        if not include_parent and result:
            result = self._remove_parent_from_list(result)
        return result

    def desa_by_kecamatan(
        self, kode: int, kode_kabupaten: int | None = None, include_parent: bool = False
    ) -> list[dict[str, Any]] | None:
        """Return villages for *kode* district, or ``None`` if unknown.

        If *kode_kabupaten* is provided, also validates that *kode* belongs to
        that regency; returns ``None`` when the hierarchy does not match.
        """
        item: dict[str, Any] | None = self._kecamatan_idx.get(kode)
        if item is None:
            return None
        if kode_kabupaten is not None and item["parent"]["kode"] != kode_kabupaten:
            return None
        result = self._desa_by_kec.get(kode, [])
        if not include_parent and result:
            result = self._remove_parent_from_list(result)
        return result

    def provinsi_exists(self, kode: int) -> bool:
        """Return ``True`` if *kode* is a known province code."""
        return kode in self._provinsi_idx

    def kabupaten_in_provinsi(self, kode_kabupaten: int, kode_provinsi: int) -> bool:
        """Return ``True`` if *kode_kabupaten* exists and belongs to *kode_provinsi*."""
        entry: dict[str, Any] | None = self._kabupaten_idx.get(kode_kabupaten)
        return entry is not None and entry["parent"]["kode"] == kode_provinsi

    def kecamatan_in_kabupaten(self, kode_kecamatan: int, kode_kabupaten: int) -> bool:
        """Return ``True`` if *kode_kecamatan* exists and belongs to *kode_kabupaten*."""
        entry: dict[str, Any] | None = self._kecamatan_idx.get(kode_kecamatan)
        return entry is not None and entry["parent"]["kode"] == kode_kabupaten

    def find_by_code(self, kode: int) -> dict[str, Any] | None:
        """Return the administrative region data for *kode*, or ``None`` if not found.

        This method searches across all administrative levels (provinsi, kabupaten,
        kecamatan, desa) and returns the matching entry with its data.
        """
        return self._all_codes_idx.get(kode)


@lru_cache(maxsize=None)
def get_loader() -> DataLoader:
    """Return the singleton :class:`DataLoader`, creating it on first call.

    Defers file I/O until the first request so that importing this module
    does not eagerly read all JSON datasets (including the large
    ``desa.json``), reducing cold-start time and memory usage on
    serverless platforms such as Vercel.  Thread safety is provided by
    :func:`functools.lru_cache`.
    """
    return DataLoader()

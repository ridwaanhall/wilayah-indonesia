import json
from functools import lru_cache
from pathlib import Path

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
        self._provinsi: list[dict] = self._read("provinsi.json")
        self._kabupaten: list[dict] = self._read("kabupaten.json")
        self._kecamatan: list[dict] = self._read("kecamatan.json")
        self._desa: list[dict] = self._read("desa.json")

        self._provinsi_idx: dict[int, dict] = {
            item["kode"]: item for item in self._provinsi
        }

        self._kabupaten_idx: dict[int, dict] = {
            item["kode"]: item for item in self._kabupaten
        }
        self._kabupaten_by_prov: dict[int, list[dict]] = {}
        for item in self._kabupaten:
            self._kabupaten_by_prov.setdefault(item["provinsi"], []).append(item)

        self._kecamatan_idx: dict[int, dict] = {
            item["kode"]: item for item in self._kecamatan
        }
        self._kecamatan_by_kab: dict[int, list[dict]] = {}
        for item in self._kecamatan:
            self._kecamatan_by_kab.setdefault(item["kabupaten"], []).append(item)

        self._desa_by_kec: dict[int, list[dict]] = {}
        for item in self._desa:
            self._desa_by_kec.setdefault(item["kecamatan"], []).append(item)

    @staticmethod
    def _read(filename: str) -> list[dict]:
        with open(DATA_DIR / filename, encoding="utf-8") as f:
            return json.load(f)

    @property
    def provinsi_list(self) -> list[dict]:
        """Return the full list of provinces."""
        return self._provinsi

    def kabupaten_by_provinsi(self, kode: int) -> list[dict] | None:
        """Return regencies/cities for *kode* province, or ``None`` if unknown."""
        if kode not in self._provinsi_idx:
            return None
        return self._kabupaten_by_prov.get(kode, [])

    def kecamatan_by_kabupaten(self, kode: int) -> list[dict] | None:
        """Return districts for *kode* regency, or ``None`` if unknown."""
        if kode not in self._kabupaten_idx:
            return None
        return self._kecamatan_by_kab.get(kode, [])

    def desa_by_kecamatan(self, kode: int) -> list[dict] | None:
        """Return villages for *kode* district, or ``None`` if unknown."""
        if kode not in self._kecamatan_idx:
            return None
        return self._desa_by_kec.get(kode, [])


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

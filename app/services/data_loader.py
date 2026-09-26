"""In-memory index of the Indonesian administrative region dataset."""

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent / "data"
DATA_FILES: tuple[str, ...] = ("provinsi.json", "kabupaten.json", "kecamatan.json", "desa.json")

# Code 0 is the national root: its children are the provinces, as in GET /api/0.
ROOT_CODE = 0

LEVEL_TYPES: dict[int, str] = {1: "province", 2: "regency", 3: "district", 4: "village"}
VILLAGE_KINDS: dict[str, str] = {"1": "kelurahan", "2": "desa", "3": "desa_adat"}
KIND_KEYS: tuple[str, ...] = ("kabupaten", "kota", "desa", "kelurahan", "desa_adat")


def region_kind(code: int, depth: int) -> str | None:
    """Classify regencies and villages by the official code convention.

    Regency segments 71-99 are cities (kota). The first digit of a village's
    4-digit segment is 1 for kelurahan, 2 for desa and 3 for desa adat.
    Names are not reliable for this: KOTAWARINGIN BARAT is a kabupaten.
    """
    text = str(code)
    if depth == 2:
        return "kota" if int(text[2:4]) >= 71 else "kabupaten"
    if depth == 4:
        return VILLAGE_KINDS.get(text[6])
    return None


class DataLoader:
    """Loads the dataset once and indexes it by code, parent and descendant counts."""

    def __init__(self) -> None:
        self.regions: dict[int, dict[str, Any]] = {}
        self.children: dict[int, list[dict[str, Any]]] = {}
        self.levels: dict[int, Counter[str]] = {}
        self.kinds: dict[int, Counter[str]] = {}

        for filename in DATA_FILES:
            with open(DATA_DIR / filename, encoding="utf-8") as file_handle:
                for item in json.load(file_handle):
                    self._index(item)

    def _index(self, item: dict[str, Any]) -> None:
        code = item["kode"]
        depth = item["tingkat"]
        parent_code = item["parent"]["kode"] if "parent" in item else ROOT_CODE

        self.regions[code] = item
        self.children.setdefault(parent_code, []).append(item)

        level = LEVEL_TYPES[depth]
        kind = region_kind(code, depth)
        # Parents are indexed before children, so every ancestor is already known.
        ancestor: int | None = parent_code
        while ancestor is not None:
            self.levels.setdefault(ancestor, Counter())[level] += 1
            if kind:
                self.kinds.setdefault(ancestor, Counter())[kind] += 1
            ancestor = self.parent_code(ancestor)

    def parent_code(self, code: int) -> int | None:
        """Return the parent code, ROOT_CODE for provinces, None for the root."""
        if code == ROOT_CODE:
            return None
        parent = self.regions[code].get("parent")
        return parent["kode"] if parent else ROOT_CODE

    def get(self, code: int) -> dict[str, Any] | None:
        return self.regions.get(code)

    def children_of(self, code: int) -> list[dict[str, Any]]:
        return self.children.get(code, [])

    def is_child(self, code: int, parent_code: int) -> bool:
        return code in self.regions and self.parent_code(code) == parent_code

    def counts(self, code: int) -> dict[str, dict[str, int]]:
        """Return descendant totals per level and per kind, with zeros filled in."""
        levels = self.levels.get(code, Counter())
        kinds = self.kinds.get(code, Counter())
        return {
            "levels": {level: levels[level] for level in LEVEL_TYPES.values()},
            "kinds": {kind: kinds[kind] for kind in KIND_KEYS},
        }


@lru_cache(maxsize=1)
def get_loader() -> DataLoader:
    return DataLoader()

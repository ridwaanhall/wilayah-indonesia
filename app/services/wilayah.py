"""Service layer for wilayah lookups, hierarchy validation and statistics."""

from typing import Any

from app.core.errors import ApiException
from app.services.data_loader import LEVEL_TYPES, ROOT_CODE, DataLoader

CODE_LENGTHS: dict[int, int] = {1: 2, 2: 4, 3: 6, 4: 10}
SEGMENT_WIDTHS: tuple[int, ...] = (2, 2, 2, 4)
CHAIN_PARAMS: tuple[str, ...] = ("kode_provinsi", "kode_kabupaten", "kode_kecamatan", "kode_desa")
LEVEL_NOT_FOUND: dict[int, str] = {
    1: "PROVINCE_NOT_FOUND",
    2: "REGENCY_NOT_FOUND",
    3: "DISTRICT_NOT_FOUND",
    4: "VILLAGE_NOT_FOUND",
}


def short_code(code: int, depth: int) -> str:
    """Format a full code as slash-separated segments, e.g. 3301012001 -> 33/01/01/2001."""
    text = f"{code:0{CODE_LENGTHS[depth]}d}"
    bounds = (0, 2, 4, 6, 10)[: depth + 1]
    return "/".join(text[start:end] for start, end in zip(bounds, bounds[1:]))


def _invalid_code(name: str, value: int, rule: str, detail: str, message: str) -> ApiException:
    return ApiException(
        "INVALID_REGION_CODE",
        detail,
        [{"field": name, "value": value, "rule": rule, "message": message}],
    )


class WilayahService:
    """Every endpoint resolves regions through this class, so the rules live in one place."""

    def __init__(self, loader: DataLoader) -> None:
        self.loader = loader

    def _parent(self, item: dict[str, Any], full_chain: bool) -> dict[str, Any] | None:
        parent_ref = item.get("parent")
        if parent_ref is None:
            return None
        parent = self.loader.regions[parent_ref["kode"]]
        return {
            "code": parent["kode"],
            "short_code": short_code(parent["kode"], parent["tingkat"]),
            "name": parent["nama"],
            "depth": parent["tingkat"],
            "type": LEVEL_TYPES[parent["tingkat"]],
            "parent": self._parent(parent, full_chain) if full_chain else None,
        }

    def _region(self, item: dict[str, Any], *, include_parent: bool, full_chain: bool) -> dict[str, Any]:
        return {
            "code": item["kode"],
            "short_code": short_code(item["kode"], item["tingkat"]),
            "name": item["nama"],
            "depth": item["tingkat"],
            "type": LEVEL_TYPES[item["tingkat"]],
            "has_children": bool(self.loader.children_of(item["kode"])),
            "parent": self._parent(item, full_chain) if include_parent else None,
        }

    def _resolve_chain(self, codes: list[int]) -> int:
        """Validate a province-first chain of full codes and return the deepest code.

        All lengths are checked before existence so a malformed request is
        reported as 422 even when an earlier segment is also unknown.
        """
        for depth, (name, code) in enumerate(zip(CHAIN_PARAMS, codes), start=1):
            length = CODE_LENGTHS[depth]
            if len(str(code)) != length:
                raise _invalid_code(
                    name,
                    code,
                    f"digits:{length}",
                    f"Parameter {name} must be a {length}-digit numeric code. Received: {code}.",
                    f"{name} must contain exactly {length} digits.",
                )

        parent_code = ROOT_CODE
        for depth, code in enumerate(codes, start=1):
            if not self.loader.is_child(code, parent_code):
                scope = (
                    f" under {LEVEL_TYPES[depth - 1]} {parent_code}" if parent_code != ROOT_CODE else ""
                )
                raise ApiException(
                    LEVEL_NOT_FOUND[depth],
                    f"No {LEVEL_TYPES[depth]} with code {code} exists{scope} in the national reference dataset.",
                )
            parent_code = code
        return parent_code

    def _lookup(self, code: int) -> dict[str, Any]:
        """Return the raw item for a code; ROOT_CODE (Indonesia) returns an empty dict."""
        if code != ROOT_CODE and len(str(code)) not in CODE_LENGTHS.values():
            raise _invalid_code(
                "kode",
                code,
                "digits:2|4|6|10",
                "Parameter kode must use one of the supported code lengths: "
                "2 (province), 4 (regency), 6 (district), or 10 (village).",
                "kode must be 2, 4, 6, or 10 digits.",
            )
        item = self.loader.get(code)
        if item is None and code != ROOT_CODE:
            raise ApiException(
                "REGION_NOT_FOUND",
                f"No region with code {code} exists in the national reference dataset.",
            )
        return item or {}

    def list_children(self, codes: list[int], *, include_parent: bool) -> list[dict[str, Any]]:
        """List the direct children of a full-code chain; an empty chain lists provinces."""
        parent_code = self._resolve_chain(codes)
        return [
            self._region(item, include_parent=include_parent, full_chain=False)
            for item in self.loader.children_of(parent_code)
        ]

    def resolve_short(self, segments: list[int], *, include_parent: bool) -> dict[str, Any]:
        """Resolve shorthand segments such as (33, 1, 1, 2001) into one region."""
        prefix = ""
        codes: list[int] = []
        for segment, width in zip(segments, SEGMENT_WIDTHS):
            prefix += f"{segment:0{width}d}"
            codes.append(int(prefix))
        return self.search_by_code(self._resolve_chain(codes), include_parent=include_parent)

    def search_by_code(self, code: int, *, include_parent: bool) -> dict[str, Any]:
        """Return any region by full code, with its complete parent chain when requested."""
        return self._region(self._lookup(code), include_parent=include_parent, full_chain=True)

    def stats(self, code: int) -> dict[str, Any]:
        """Return descendant totals for a region (0 = Indonesia) and for each direct child."""
        item = self._lookup(code)
        return {
            "region": self._region(item, include_parent=True, full_chain=True) if item else None,
            **self.loader.counts(code),
            "children": [
                {
                    "region": self._region(child, include_parent=False, full_chain=False),
                    **self.loader.counts(child["kode"]),
                }
                for child in self.loader.children_of(code)
            ],
        }

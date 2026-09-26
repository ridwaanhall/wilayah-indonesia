"""Tests for the DataLoader index."""

from app.services.data_loader import ROOT_CODE, get_loader, region_kind


def test_get_loader_is_cached() -> None:
    assert get_loader() is get_loader()


def test_every_level_is_indexed() -> None:
    loader = get_loader()
    assert loader.get(11)["nama"] == "ACEH"
    assert loader.get(1101)["tingkat"] == 2
    assert loader.get(110101)["tingkat"] == 3
    assert loader.get(1101012001)["tingkat"] == 4
    assert loader.get(99) is None


def test_root_children_are_provinces() -> None:
    provinces = get_loader().children_of(ROOT_CODE)
    assert len(provinces) == 38
    assert all(item["tingkat"] == 1 for item in provinces)


def test_children_of_follow_parent_codes() -> None:
    loader = get_loader()
    assert all(item["parent"]["kode"] == 11 for item in loader.children_of(11))
    assert all(item["parent"]["kode"] == 1101 for item in loader.children_of(1101))
    assert loader.children_of(1101012001) == []


def test_is_child() -> None:
    loader = get_loader()
    assert loader.is_child(11, ROOT_CODE)
    assert loader.is_child(1101, 11)
    assert not loader.is_child(1101, 12)
    assert not loader.is_child(9999, 11)


def test_parent_code() -> None:
    loader = get_loader()
    assert loader.parent_code(ROOT_CODE) is None
    assert loader.parent_code(11) == ROOT_CODE
    assert loader.parent_code(1101012001) == 110101


def test_national_counts_match_dataset() -> None:
    counts = get_loader().counts(ROOT_CODE)
    assert counts["levels"] == {"province": 38, "regency": 514, "district": 7277, "village": 83731}
    assert counts["kinds"]["kabupaten"] + counts["kinds"]["kota"] == 514
    assert sum(counts["kinds"][key] for key in ("desa", "kelurahan", "desa_adat")) == 83731


def test_counts_for_leaf_are_zero() -> None:
    counts = get_loader().counts(1101012001)
    assert set(counts["levels"].values()) == {0}
    assert set(counts["kinds"].values()) == {0}


def test_region_kind_uses_codes_not_names() -> None:
    assert region_kind(6201, 2) == "kabupaten"  # KOTAWARINGIN BARAT
    assert region_kind(1171, 2) == "kota"
    assert region_kind(1101012001, 4) == "desa"
    assert region_kind(1171011001, 4) == "kelurahan"
    assert region_kind(9103013007, 4) == "desa_adat"
    assert region_kind(11, 1) is None

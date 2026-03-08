import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=1)
def load_provinsi():
    with open(DATA_DIR / "provinsi.json", "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_kabupaten():
    with open(DATA_DIR / "kabupaten.json", "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_kecamatan():
    with open(DATA_DIR / "kecamatan.json", "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_desa():
    with open(DATA_DIR / "desa.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_provinsi_list():
    return load_provinsi()


def get_kabupaten_by_provinsi(kode_provinsi):
    return [k for k in load_kabupaten() if k["provinsi"] == kode_provinsi]


def get_kecamatan_by_kabupaten(kode_kabupaten):
    return [k for k in load_kecamatan() if k["kabupaten"] == kode_kabupaten]


def get_desa_by_kecamatan(kode_kecamatan):
    return [d for d in load_desa() if d["kecamatan"] == kode_kecamatan]


def provinsi_exists(kode_provinsi):
    return any(p["kode"] == kode_provinsi for p in load_provinsi())


def kabupaten_exists(kode_kabupaten):
    return any(k["kode"] == kode_kabupaten for k in load_kabupaten())


def kecamatan_exists(kode_kecamatan):
    return any(k["kode"] == kode_kecamatan for k in load_kecamatan())

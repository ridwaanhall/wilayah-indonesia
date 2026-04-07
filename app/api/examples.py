"""OpenAPI examples for consistent API documentation."""

SIMPLE_PROVINSI_EXAMPLE: dict[str, object] = {
    "success": True,
    "message": "Data provinsi berhasil ditemukan.",
    "data": {
        "kode_lengkap": 11,
        "kode_singkat": "11",
        "kode": 11,
        "nama": "ACEH",
        "tingkat": 1,
        "level": "provinsi",
        "parent": None,
    },
}

SIMPLE_KABUPATEN_EXAMPLE: dict[str, object] = {
    "success": True,
    "message": "Data kabupaten/kota berhasil ditemukan.",
    "data": {
        "kode_lengkap": 1101,
        "kode_singkat": "11/01",
        "kode": 1101,
        "nama": "KABUPATEN ACEH SELATAN",
        "tingkat": 2,
        "level": "kabupaten",
        "parent": {
            "kode": 11,
            "nama": "ACEH",
            "tingkat": 1,
        },
    },
}

SIMPLE_KECAMATAN_EXAMPLE: dict[str, object] = {
    "success": True,
    "message": "Data kecamatan berhasil ditemukan.",
    "data": {
        "kode_lengkap": 110101,
        "kode_singkat": "11/01/01",
        "kode": 110101,
        "nama": "BAKONGAN",
        "tingkat": 3,
        "level": "kecamatan",
        "parent": {
            "kode": 1101,
            "nama": "KABUPATEN ACEH SELATAN",
            "tingkat": 2,
        },
    },
}

ERROR_NOT_FOUND_EXAMPLE: dict[str, str] = {
    "detail": "Data wilayah yang diminta tidak tersedia pada basis data referensi nasional.",
}

ERROR_VALIDATION_EXAMPLE: dict[str, str] = {
    "detail": "Parameter permintaan tidak valid. Periksa kembali format kode wilayah.",
}

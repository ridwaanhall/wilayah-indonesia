"""OpenAPI examples for consistent API documentation."""

from app.core.config import get_settings

API_VERSION = get_settings().api_version

SIMPLE_REGION_EXAMPLE: dict[str, object] = {
    "success": True,
    "data": {
        "code": 110101,
        "short_code": "11/01/01",
        "name": "BAKONGAN",
        "depth": 3,
        "type": "district",
        "has_children": True,
        "parent": {
            "code": 1101,
            "short_code": "11/01",
            "name": "ACEH SELATAN",
            "depth": 2,
            "type": "regency",
            "parent": {
                "code": 11,
                "short_code": "11",
                "name": "ACEH",
                "depth": 1,
                "type": "province",
                "parent": None,
            },
        },
    },
    "error": None,
    "meta": {
        "api_version": API_VERSION,
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "01HZ9QXMBF3RVTKNE8D4J7WQCX",
        "duration_ms": 11,
    },
}

ERROR_NOT_FOUND_EXAMPLE: dict[str, object] = {
    "success": False,
    "data": None,
    "error": {
        "code": "REGION_NOT_FOUND",
        "message": "The requested region could not be found.",
        "detail": "No region with code 330999 exists in the national reference dataset.",
        "hint": "Verify the region code using GET /api/0 for valid province codes.",
        "docs": "/docs/errors#REGION_NOT_FOUND",
        "fields": None,
    },
    "meta": {
        "api_version": API_VERSION,
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "01HZ9U00000000000000000000",
        "duration_ms": 4,
    },
}

ERROR_VALIDATION_EXAMPLE: dict[str, object] = {
    "success": False,
    "data": None,
    "error": {
        "code": "VALIDATION_FAILED",
        "message": "One or more request parameters are invalid.",
        "detail": "Parameter validation failed for incoming request.",
        "hint": "Check the fields array for per-field details.",
        "docs": "/docs/errors#VALIDATION_FAILED",
        "fields": [
            {
                "field": "kode_provinsi",
                "value": "33XY",
                "rule": "numeric",
                "message": "kode_provinsi must be a 2-digit numeric integer between 11 and 99.",
            }
        ],
    },
    "meta": {
        "api_version": API_VERSION,
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "01HZ9V00000000000000000000",
        "duration_ms": 2,
    },
}

LIST_REGION_EXAMPLE: dict[str, object] = {
    "success": True,
    "data": {
        "items": [
            {
                "code": 11,
                "short_code": "11",
                "name": "ACEH",
                "depth": 1,
                "type": "province",
                "has_children": True,
                "parent": None,
            }
        ],
        "pagination": {
            "total": 38,
            "per_page": 38,
            "has_next": False,
            "has_prev": False,
            "next_cursor": None,
            "prev_cursor": None,
        },
    },
    "error": None,
    "meta": {
        "api_version": API_VERSION,
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "01HZ9R00000000000000000000",
        "duration_ms": 9,
    },
}

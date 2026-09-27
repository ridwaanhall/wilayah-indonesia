"""OpenAPI examples and response declarations shared by every data endpoint."""

from typing import Any

from app.core.config import get_settings
from app.schemas.common import ErrorResponse


def _meta(duration_ms: int) -> dict[str, Any]:
    return {
        "api_version": get_settings().api_version,
        "timestamp": "2026-04-08T04:30:00Z",
        "request_id": "01HZ9QXMBF3RVTKNE8D4J7WQCX",
        "duration_ms": duration_ms,
    }


def _success(data: dict[str, Any]) -> dict[str, Any]:
    return {"success": True, "data": data, "error": None, "meta": _meta(3)}


def _error(code: str, message: str, detail: str, hint: str, fields: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "success": False,
        "data": None,
        "error": {
            "code": code,
            "message": message,
            "detail": detail,
            "hint": hint,
            "docs": f"https://wilayah.rone.dev/docs/errors#{code}",
            "fields": fields,
        },
        "meta": _meta(1),
    }


_PROVINCE = {"code": 33, "short_code": "33", "name": "JAWA TENGAH", "depth": 1, "type": "province"}

REGION_EXAMPLE = _success(
    {
        "code": 330101,
        "short_code": "33/01/01",
        "name": "KEDUNGREJA",
        "depth": 3,
        "type": "district",
        "has_children": True,
        "parent": {
            "code": 3301,
            "short_code": "33/01",
            "name": "CILACAP",
            "depth": 2,
            "type": "regency",
            "parent": {**_PROVINCE, "parent": None},
        },
    }
)

LIST_EXAMPLE = _success(
    {
        "items": [{**_PROVINCE, "has_children": True, "parent": None}],
        "pagination": {
            "total": 1,
            "per_page": 1,
            "has_next": False,
            "has_prev": False,
            "next_cursor": None,
            "prev_cursor": None,
        },
    }
)

STATS_EXAMPLE = _success(
    {
        "region": {**_PROVINCE, "has_children": True, "parent": None},
        "levels": {"province": 0, "regency": 35, "district": 576, "village": 8563},
        "kinds": {"regency": 29, "city": 6, "rural_village": 7810, "urban_village": 753, "customary_village": 0},
        "children": [
            {
                "region": {
                    "code": 3301,
                    "short_code": "33/01",
                    "name": "CILACAP",
                    "depth": 2,
                    "type": "regency",
                    "has_children": True,
                    "parent": None,
                },
                "levels": {"province": 0, "regency": 0, "district": 24, "village": 284},
                "kinds": {"regency": 0, "city": 0, "rural_village": 269, "urban_village": 15, "customary_village": 0},
            }
        ],
    }
)

_NOT_FOUND_EXAMPLE = _error(
    "REGION_NOT_FOUND",
    "The requested region could not be found.",
    "No region with code 330999 exists in the national reference dataset.",
    "Verify the region code using GET /api/0 for valid province codes.",
    None,
)

_VALIDATION_EXAMPLE = _error(
    "INVALID_REGION_CODE",
    "The region code format is invalid.",
    "Parameter regency_code must be a 4-digit numeric code. Received: 1.",
    "Use 2 digits for a province, 4 for a regency, 6 for a district, or 10 for a village.",
    [{"field": "regency_code", "value": 1, "rule": "digits:4", "message": "regency_code must contain exactly 4 digits."}],
)


def responses(example: dict[str, Any]) -> dict[int | str, dict[str, Any]]:
    """Declare the success example plus the shared 404 and 422 error envelopes."""
    return {
        200: {"description": "Success.", "content": {"application/json": {"example": example}}},
        404: {
            "model": ErrorResponse,
            "description": "Region not found.",
            "content": {"application/json": {"example": _NOT_FOUND_EXAMPLE}},
        },
        422: {
            "model": ErrorResponse,
            "description": "Invalid code or parameter.",
            "content": {"application/json": {"example": _VALIDATION_EXAMPLE}},
        },
    }

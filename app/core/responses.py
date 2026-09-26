"""Response helpers for the standard API envelope."""

from datetime import datetime, timezone
import time
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.errors import ERRORS


def _meta_from_request(request: Request) -> dict[str, Any]:
    start_time = getattr(request.state, "start_time", time.perf_counter())
    return {
        "api_version": get_settings().api_version,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "request_id": getattr(request.state, "request_id", str(uuid.uuid4())),
        "duration_ms": max(int((time.perf_counter() - start_time) * 1000), 0),
    }


def _envelope(request: Request, status_code: int, data: Any, error: dict[str, Any] | None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": error is None,
            "data": data,
            "error": error,
            "meta": _meta_from_request(request),
        },
    )


def success_response(request: Request, data: Any) -> JSONResponse:
    """Return a success envelope for object payloads."""
    return _envelope(request, 200, data, None)


def list_response(request: Request, items: list[dict[str, Any]]) -> JSONResponse:
    """Return a success envelope for a complete, unpaginated list."""
    total = len(items)
    pagination = {
        "total": total,
        "per_page": total,
        "has_next": False,
        "has_prev": False,
        "next_cursor": None,
        "prev_cursor": None,
    }
    return _envelope(request, 200, {"items": items, "pagination": pagination}, None)


def error_response(
    request: Request,
    code: str,
    detail: str,
    fields: list[dict[str, Any]] | None = None,
    status_code: int | None = None,
) -> JSONResponse:
    """Return an error envelope for a catalogued error code."""
    spec = ERRORS[code]
    error = {
        "code": code,
        "message": spec.message,
        "detail": detail,
        "hint": spec.hint,
        "docs": f"{str(request.base_url).rstrip('/')}/docs/errors#{code}",
        "fields": fields,
    }
    return _envelope(request, status_code or spec.status, None, error)

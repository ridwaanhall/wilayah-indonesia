"""Response helpers for handbook-compliant API envelopes."""

from datetime import datetime, timezone
import time
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

ERROR_DOCS_BASE_URL = "https://api.yourapp.com/docs/errors"


def _meta_from_request(request: Request) -> dict[str, Any]:
    start_time = getattr(request.state, "start_time", time.perf_counter())
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    return {
        "api_version": "v3",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "request_id": request_id,
        "duration_ms": max(int((time.perf_counter() - start_time) * 1000), 0),
    }


def build_pagination(total: int) -> dict[str, Any]:
    """Create a stable pagination block for non-cursor list responses."""
    return {
        "total": total,
        "per_page": total,
        "has_next": False,
        "has_prev": False,
        "next_cursor": None,
        "prev_cursor": None,
    }


def success_response(
    request: Request,
    data: Any,
    status_code: int = 200,
) -> JSONResponse:
    """Return a success envelope for object payloads."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
            "error": None,
            "meta": _meta_from_request(request),
        },
    )


def list_response(
    request: Request,
    items: list[dict[str, Any]],
    status_code: int = 200,
) -> JSONResponse:
    """Return a success envelope for list payloads with pagination."""
    return success_response(
        request=request,
        status_code=status_code,
        data={
            "items": items,
            "pagination": build_pagination(total=len(items)),
        },
    )


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    detail: str,
    hint: str,
    fields: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    """Return a handbook-compliant error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": code,
                "message": message,
                "detail": detail,
                "hint": hint,
                "docs": f"{ERROR_DOCS_BASE_URL}#{code}",
                "fields": fields,
            },
            "meta": _meta_from_request(request),
        },
    )

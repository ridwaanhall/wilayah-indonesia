from collections.abc import Awaitable, Callable
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.core.errors import ApiException
from app.core.responses import error_response

NO_STORE_PATHS = frozenset({"/docs", "/redoc", "/openapi.json"})
HTTP_ERROR_CODES = {404: "RESOURCE_NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def register_http_middleware(app: FastAPI) -> None:
    """Register middleware that applies security and caching headers."""

    @app.middleware("http")
    async def security_headers(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.start_time = time.perf_counter()
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "interest-cohort=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        response.headers.setdefault(
            "Cache-Control",
            "no-store" if request.url.path in NO_STORE_PATHS else "public, max-age=86400, s-maxage=86400",
        )
        return response


def _validation_fields(exc: RequestValidationError) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for err in exc.errors():
        location = [str(value) for value in err.get("loc", ()) if value not in {"path", "query", "body"}]
        fields.append(
            {
                "field": ".".join(location) if location else "request",
                "value": err.get("input"),
                "rule": str(err.get("type", "validation_error")),
                "message": str(err.get("msg", "Invalid value")),
            }
        )
    return fields


def register_exception_handlers(app: FastAPI) -> None:
    """Register app-wide exception handlers with consistent response payloads."""

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
        return error_response(request, exc.code, str(exc.detail), exc.fields)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = HTTP_ERROR_CODES.get(exc.status_code, "INTERNAL_ERROR")
        return error_response(request, code, str(exc.detail), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(request, "VALIDATION_FAILED", "Request validation failed.", _validation_fields(exc))

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return error_response(
            request,
            "INTERNAL_ERROR",
            "An unhandled exception occurred while processing the request.",
        )

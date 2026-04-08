from collections.abc import Awaitable, Callable
import time
import uuid
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response

from app.core.errors import ApiException
from app.core.responses import error_response


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
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )

        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json"):
            response.headers["Cache-Control"] = "no-store"
        else:
            response.headers["Cache-Control"] = "public, max-age=86400, s-maxage=86400"
        return response


def register_exception_handlers(app: FastAPI) -> None:
    """Register app-wide exception handlers with consistent response payloads."""

    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
        return error_response(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            detail=str(exc.detail),
            hint=exc.hint,
            fields=exc.fields,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = str(exc.detail)
        if isinstance(exc.detail, dict):
            detail = str(exc.detail.get("detail", exc.detail))

        return error_response(
            request,
            status_code=exc.status_code,
            code="REGION_NOT_FOUND" if exc.status_code == status.HTTP_404_NOT_FOUND else "INTERNAL_ERROR",
            message=(
                "The requested resource could not be found."
                if exc.status_code == status.HTTP_404_NOT_FOUND
                else "An unexpected error occurred."
            ),
            detail=detail,
            hint=(
                "Verify the request path and region code."
                if exc.status_code == status.HTTP_404_NOT_FOUND
                else "Please try again. If the issue persists, contact support."
            ),
            fields=None,
        )

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

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            code="VALIDATION_FAILED",
            message="One or more request parameters are invalid.",
            detail="Parameter validation failed for the incoming request.",
            hint="Check the fields array for per-field validation details.",
            fields=_validation_fields(exc),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        return error_response(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR",
            message="An unexpected error occurred.",
            detail="An unhandled exception occurred while processing the request.",
            hint="Please try again. If the issue persists, contact support.",
            fields=None,
        )

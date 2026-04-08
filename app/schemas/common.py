"""Shared API response schema definitions."""

from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

TData = TypeVar("TData")


class MetaInfo(BaseModel):
    """Metadata included in every API response."""

    api_version: str = Field(description="API version identifier", examples=["v3"])
    timestamp: str = Field(description="ISO 8601 UTC timestamp")
    request_id: str = Field(description="Unique request identifier")
    duration_ms: int = Field(ge=0, description="Server processing duration in milliseconds")


class ValidationField(BaseModel):
    """Per-field validation error details."""

    field: str
    value: Any
    rule: str
    message: str


class ErrorInfo(BaseModel):
    """Standardized error shape inside the response envelope."""

    code: str
    message: str
    detail: str
    hint: str
    docs: str
    fields: list[ValidationField] | None = None


class PaginationInfo(BaseModel):
    """Pagination payload used by all list endpoints."""

    total: int = Field(ge=0)
    per_page: int = Field(ge=0)
    has_next: bool
    has_prev: bool
    next_cursor: str | None = None
    prev_cursor: str | None = None


class ApiEnvelope(BaseModel):
    """Universal top-level API response envelope."""

    success: bool
    data: Any | None
    error: ErrorInfo | None
    meta: MetaInfo


class SuccessResponse(BaseModel, Generic[TData]):
    """Typed success envelope for explicit OpenAPI data contracts."""

    success: Literal[True] = True
    data: TData
    error: None = None
    meta: MetaInfo


class ErrorResponse(BaseModel):
    """Typed error envelope for explicit OpenAPI error contracts."""

    success: Literal[False] = False
    data: None = None
    error: ErrorInfo
    meta: MetaInfo

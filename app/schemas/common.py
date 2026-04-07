from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str


class ErrorResponse(BaseModel):
    """Standardized professional error response schema."""

    detail: str

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Standard error response body."""

    detail: str

"""Custom API exception definitions."""

from typing import Any

from fastapi import HTTPException


class ApiException(HTTPException):
    """HTTP exception with handbook-compliant error metadata."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        detail: str,
        hint: str,
        fields: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.code = code
        self.message = message
        self.hint = hint
        self.fields = fields

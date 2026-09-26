"""Error catalog and the API exception that references it."""

from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException


@dataclass(frozen=True)
class ErrorSpec:
    """Stable metadata for one error code."""

    status: int
    message: str
    hint: str
    description: str


ERRORS: dict[str, ErrorSpec] = {
    "INVALID_REGION_CODE": ErrorSpec(
        422,
        "The region code format is invalid.",
        "Use 2 digits for a province, 4 for a regency, 6 for a district, or 10 for a village.",
        "A code has the wrong number of digits for the level it is used at.",
    ),
    "VALIDATION_FAILED": ErrorSpec(
        422,
        "One or more request parameters are invalid.",
        "Fix the invalid request parameters and try again. See fields for details.",
        "A path or query parameter is not a number, or is outside its allowed range.",
    ),
    "REGION_NOT_FOUND": ErrorSpec(
        404,
        "The requested region could not be found.",
        "Verify the region code using GET /api/0 for valid province codes.",
        "The code is well formed but no region in the dataset uses it.",
    ),
    "PROVINCE_NOT_FOUND": ErrorSpec(
        404,
        "The requested province could not be found.",
        "Verify the province code with GET /api/0.",
        "No province uses the given province code.",
    ),
    "REGENCY_NOT_FOUND": ErrorSpec(
        404,
        "The requested regency could not be found.",
        "Check that the regency belongs to the given province.",
        "No regency or city with that code exists under the given province.",
    ),
    "DISTRICT_NOT_FOUND": ErrorSpec(
        404,
        "The requested district could not be found.",
        "Check that the district belongs to the given regency.",
        "No district with that code exists under the given regency or city.",
    ),
    "VILLAGE_NOT_FOUND": ErrorSpec(
        404,
        "The requested village could not be found.",
        "Check that the village belongs to the given district.",
        "No village with that code exists under the given district.",
    ),
    "RESOURCE_NOT_FOUND": ErrorSpec(
        404,
        "The requested resource could not be found.",
        "Verify the request path. GET /api/ lists every endpoint.",
        "The path does not match any endpoint.",
    ),
    "METHOD_NOT_ALLOWED": ErrorSpec(
        405,
        "The request method is not allowed.",
        "This API is read-only. Use GET.",
        "The endpoint exists but only answers GET requests.",
    ),
    "INTERNAL_ERROR": ErrorSpec(
        500,
        "An unexpected error occurred.",
        "Please try again. If the issue persists, contact support.",
        "Something failed on the server. Retrying is safe; every endpoint is read-only.",
    ),
}


class ApiException(HTTPException):
    """HTTP exception carrying a catalogued error code."""

    def __init__(self, code: str, detail: str, fields: list[dict[str, Any]] | None = None) -> None:
        super().__init__(status_code=ERRORS[code].status, detail=detail)
        self.code = code
        self.fields = fields

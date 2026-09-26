"""Introspection of the registered API routes, shared by /api/ and the landing page."""

from fastapi import FastAPI
from fastapi.routing import APIRoute

API_PREFIX = "/api"


def public_routes(app: FastAPI) -> list[APIRoute]:
    """Return the documented API routes in registration order."""
    return [
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.include_in_schema and route.path.startswith(API_PREFIX)
    ]

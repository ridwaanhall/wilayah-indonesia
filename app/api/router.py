from fastapi import APIRouter

from app.api.catalog import API_PREFIX
from app.api.endpoints import hierarchy, lookup, root, shorthand, stats

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(root.router)
api_router.include_router(lookup.router)
api_router.include_router(stats.router)
api_router.include_router(shorthand.router)
# Registered last: its /{province_code} pattern would otherwise capture /code, /stats and /s.
api_router.include_router(hierarchy.router)

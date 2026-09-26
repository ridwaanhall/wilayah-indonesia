from fastapi import APIRouter

from app.api.catalog import API_PREFIX
from app.api.endpoints import root, search, simple, stats, wilayah

api_router = APIRouter(prefix=API_PREFIX)
api_router.include_router(root.router)
api_router.include_router(search.router)
api_router.include_router(stats.router)
api_router.include_router(simple.router)
# Registered last: its /{kode_provinsi} pattern would otherwise capture /kode, /stats and /s.
api_router.include_router(wilayah.router)

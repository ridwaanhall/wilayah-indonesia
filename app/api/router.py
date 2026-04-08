from fastapi import APIRouter

from app.api.endpoints import root, search, simple, wilayah

api_router = APIRouter(prefix="/api")
api_router.include_router(root.router)
api_router.include_router(search.router)
api_router.include_router(simple.router)
api_router.include_router(wilayah.router)

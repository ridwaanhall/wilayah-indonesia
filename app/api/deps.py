from typing import Annotated

from fastapi import Depends

from app.services.data_loader import DataLoader, get_loader
from app.services.simple import SimpleWilayahService
from app.services.wilayah import WilayahService


def get_simple_service(loader: Annotated[DataLoader, Depends(get_loader)]) -> SimpleWilayahService:
    """Build a SimpleWilayahService instance from cached loader."""
    return SimpleWilayahService(loader)


def get_wilayah_service(loader: Annotated[DataLoader, Depends(get_loader)]) -> WilayahService:
    """Build a WilayahService instance from cached loader."""
    return WilayahService(loader)

from typing import Annotated

from fastapi import Depends, Query

from app.services.data_loader import DataLoader, get_loader
from app.services.wilayah import WilayahService


def get_wilayah_service(loader: Annotated[DataLoader, Depends(get_loader)]) -> WilayahService:
    """Build a WilayahService instance from the cached loader."""
    return WilayahService(loader)


Service = Annotated[WilayahService, Depends(get_wilayah_service)]
ChainParent = Annotated[bool, Query(description="Sertakan hierarki parent penuh (default true).")]
ItemParent = Annotated[bool, Query(description="Sertakan parent langsung pada setiap item (default false).")]

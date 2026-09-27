from typing import Annotated

from fastapi import Depends, Query

from app.services.data_loader import DataLoader, get_loader
from app.services.regions import RegionService


def get_region_service(loader: Annotated[DataLoader, Depends(get_loader)]) -> RegionService:
    """Build a RegionService instance from the cached loader."""
    return RegionService(loader)


Service = Annotated[RegionService, Depends(get_region_service)]
ChainParent = Annotated[bool, Query(description="Include the full parent chain up to the province (default true).")]
ItemParent = Annotated[bool, Query(description="Include each item's direct parent (default false).")]

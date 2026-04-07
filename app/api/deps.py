from collections.abc import Generator
from typing import Annotated

from fastapi import Depends

from app.services.data_loader import DataLoader, get_loader
from app.services.simple import SimpleWilayahService


def get_simple_service(loader: Annotated[DataLoader, Depends(get_loader)]) -> Generator[SimpleWilayahService, None, None]:
    """Build SimpleWilayahService from cached data loader."""
    yield SimpleWilayahService(loader)

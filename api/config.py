from os import getenv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    """Application configuration loaded from environment variables."""

    __slots__ = ("debug", "allowed_origins")

    def __init__(self) -> None:
        self.debug: bool = getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        raw: str = getenv("ALLOWED_ORIGINS", "")
        self.allowed_origins: list[str] = (
            [o.strip() for o in raw.split(",") if o.strip()] if raw else []
        )


settings = Settings()

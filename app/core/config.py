from functools import lru_cache
from dotenv import load_dotenv

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()  # Load environment variables from .env file at startup

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Wilayah Indonesia API"
    app_version: str = "3.0.0"
    DEBUG: bool = False
    allowed_origins: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins.strip():
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached app settings."""
    return Settings()

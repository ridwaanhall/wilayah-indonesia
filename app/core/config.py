from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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
    def api_version(self) -> str:
        """Return API version label (e.g. app_version 3.0.0 -> v3)."""
        raw = self.app_version.strip()
        normalized = raw[1:] if raw.lower().startswith("v") else raw
        major = normalized.split(".", maxsplit=1)[0]
        if major.isdigit():
            return f"v{major}"
        return raw if raw.lower().startswith("v") else f"v{raw}"

    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins.strip():
            return []
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached app settings."""
    return Settings()

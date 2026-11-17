from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration for the frontend application.

    Values are read from environment variables and an optional ``.env`` file.
    """

    app_name: str = "SmartTicket"
    app_env: str = "development"
    app_debug: bool = True
    demo_mode: bool = True
    secret_key: str = "dev-only-secret-change-in-production"
    session_cookie_name: str = "smartticket_session"
    session_max_age_seconds: int = 60 * 60 * 8

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

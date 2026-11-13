"""Runtime configuration and environment settings."""

import json
from functools import lru_cache
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings and environment configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    llm_model: str = "google/gemini-2.5-flash"
    allowed_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://fgm9000.github.io",
    ]
    rate_limit_per_minute: int = 5
    daily_request_cap: int = 200
    fake_model: bool = False

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: Any) -> list[str]:
        """Parse allowed origins from a list, JSON array string, or comma-separated string."""
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if isinstance(value, str):
            cleaned = value.strip()
            if not cleaned:
                return []
            if cleaned.startswith("[") and cleaned.endswith("]"):
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [
                            item.strip()
                            for item in parsed
                            if isinstance(item, str) and item.strip()
                        ]
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in cleaned.split(",") if item.strip()]
        return []


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]

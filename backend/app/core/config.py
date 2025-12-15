from functools import lru_cache
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Mushroom Kingdom Characters API"
    api_prefix: str = "/api"

    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: int = Field(default=3306, validation_alias="DB_PORT")
    db_name: str = Field(default="mario_chat", validation_alias="DB_NAME")
    db_user: str = Field(default="mario", validation_alias="DB_USER")
    db_password: str = Field(default="secret", validation_alias="DB_PASSWORD")
    database_url_override: Optional[str] = Field(
        default=None, validation_alias="DATABASE_URL"
    )

    allowed_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://localhost:80,http://localhost:8080",
        validation_alias="ALLOWED_ORIGINS"
    )
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from string (comma-separated) to list."""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    openai_api_key: str | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )
    
    # Guardrails configuration
    moderation_enabled: bool = Field(
        default=True,
        validation_alias="MODERATION_ENABLED"
    )
    moderation_level: str = Field(
        default="moderate",
        validation_alias="MODERATION_LEVEL"
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            return self.database_url_override
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def get_settings() -> Settings:
    """Return settings instance."""
    return Settings()


settings = get_settings()


"""Application configuration."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    app_name: str = "LLM Training Agent"
    app_version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    debug: bool = False
    cors_origins: list[str] = ["*"]
    default_provider: str = "ollama"
    database_url: str = "sqlite+aiosqlite:///./llm_training_agent.db"
    log_level: str = "INFO"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    ollama_base_url: str = "http://localhost:11434"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
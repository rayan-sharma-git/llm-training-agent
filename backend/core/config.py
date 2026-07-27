"""Application configuration using Pydantic Settings."""
from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Deployment environment."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ProviderName(str, Enum):
    """Supported AI provider names."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "LLM Training Agent"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1

    # Logging
    log_level: LogLevel = LogLevel.INFO
    log_format: str = "json"  # json or text
    log_file: Optional[str] = None

    # Database
    database_url: str = "sqlite:///./llm_training_agent.db"
    database_echo: bool = False

    # AI Provider
    default_provider: ProviderName = ProviderName.OLLAMA
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-haiku-20241022"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Analysis
    max_project_size_mb: int = 500
    max_dataset_size_mb: int = 100
    max_token_count: int = 1000000
    analysis_timeout_seconds: int = 300

    # CORS
    cors_origins: List[str] = ["*"]

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL is valid."""
        if not v:
            raise ValueError("Database URL cannot be empty")
        return v

    @field_validator("max_project_size_mb", "max_dataset_size_mb")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Ensure positive values."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Return application settings (useful for dependency injection)."""
    return settings
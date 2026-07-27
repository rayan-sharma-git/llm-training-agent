"""Application error classes and handlers."""
from __future__ import annotations

from typing import Optional


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, error_code: str, details: Optional[str] = None) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details

    def to_dict(self) -> dict[str, Optional[str]]:
        """Convert to dictionary for JSON response."""
        return {
            "errorCode": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(AppError):
    """Input validation failure."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message, "VALIDATION_ERROR", details)


class ProjectNotFoundError(AppError):
    """Project path does not exist."""

    def __init__(self, path: str) -> None:
        super().__init__(f"Project not found: {path}", "PROJECT_NOT_FOUND")


class AnalysisError(AppError):
    """Analysis pipeline failure."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message, "ANALYSIS_FAILED", details)


class ProviderError(AppError):
    """AI provider failure."""

    def __init__(self, message: str, provider: str, details: Optional[str] = None) -> None:
        super().__init__(f"{provider}: {message}", "PROVIDER_UNAVAILABLE", details)


class FileError(AppError):
    """File operation failure."""

    def __init__(self, message: str, path: str, details: Optional[str] = None) -> None:
        super().__init__(f"File error ({path}): {message}", "FILE_OPERATION_FAILED", details)


class ModificationError(AppError):
    """File modification failure."""

    def __init__(self, message: str, path: str, details: Optional[str] = None) -> None:
        super().__init__(f"Modification failed ({path}): {message}", "MODIFICATION_FAILED", details)


class StorageError(AppError):
    """Storage/database failure."""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message, "STORAGE_ERROR", details)
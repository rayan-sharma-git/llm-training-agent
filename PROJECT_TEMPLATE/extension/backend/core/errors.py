"""Application error classes."""
from __future__ import annotations

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base application error."""
    
    def __init__(self, message: str, error_code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON responses."""
        return {
            "errorCode": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class AnalysisError(AppError):
    """Analysis pipeline error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="ANALYSIS_FAILED", details=details)


class ProviderError(AppError):
    """AI provider error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="PROVIDER_UNAVAILABLE", details=details)


class ValidationError(AppError):
    """Validation error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, error_code="VALIDATION_ERROR", details=details)
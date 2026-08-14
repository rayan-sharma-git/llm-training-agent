"""Backward-compatibility alias for the AI provider interface.

The canonical ``AIProvider`` ABC now lives in ``ai/provider.py`` with the
modern ``chat_completion`` / ``validate_credentials`` / ``health_check`` /
``get_supported_models`` interface.  This module re-exports it so that any
legacy code importing ``from ai.base import AIProvider`` continues to work.
"""
from __future__ import annotations

from ai.provider import AIProvider

__all__ = ["AIProvider"]

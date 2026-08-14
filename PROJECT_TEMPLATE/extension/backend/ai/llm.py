"""LLM helper for analyzers — provides a unified interface for LLM calls with prompt templates.

Usage:
    from ai.llm import LLMHelper
    helper = LLMHelper()
    result = await helper.analyze_with_prompt(
        prompt_template="analyzers/dataset.md",
        context_data={...},
        schema={...},
    )

When no provider is configured (e.g., Ollama not running, no API keys),
the helper gracefully degrades by returning None and the analyzer
falls back to deterministic logic.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from core.config import get_settings

logger = logging.getLogger(__name__)

# Base directory for prompt templates
_PROMPTS_DIR = Path(__file__).parent / "prompts"


class LLMHelper:
    """Helper to load prompt templates and call the configured AI provider."""

    def __init__(self):
        self._provider = None

    @property
    def provider_name(self) -> str:
        from core.config import get_active_provider
        return get_active_provider()

    @property
    def is_available(self) -> bool:
        """Check whether a provider can be instantiated (does not make a network call)."""
        try:
            from ai.providers import get_provider
            self._provider = get_provider()
            return True
        except (ValueError, Exception) as e:
            logger.debug(f"Provider not available: {e}")
            return False

    @property
    def provider(self):
        """Get or create the provider instance."""
        if self._provider is None:
            from ai.providers import get_provider
            self._provider = get_provider()
        return self._provider

    def load_prompt(self, *parts: str) -> str:
        """Load a prompt template from backend/ai/prompts/.

        Args:
            *parts: Path parts, e.g. "analyzers", "dataset.md"
        """
        path = _PROMPTS_DIR.joinpath(*parts)
        return path.read_text(encoding="utf-8")

    def load_system_prompt(self) -> str:
        """Load the analyst system prompt."""
        return self.load_prompt("system", "analyst.md")

    async def call(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> Optional[str]:
        """Call the LLM and return the raw text response.

        Returns None if the provider is unavailable or the call fails.
        """
        if not self.is_available:
            logger.info("LLM provider not available; skipping LLM call.")
            return None

        messages = [{"role": "user", "content": prompt}]
        system = self.load_system_prompt()

        try:
            response = await self.provider.chat_completion(
                messages, system=system, temperature=temperature
            )
            return response.get("content", "")
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            return None

    async def call_structured(
        self,
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
    ) -> Optional[Dict[str, Any]]:
        """Call the LLM and request structured JSON output.

        Returns None if the provider is unavailable or the call fails.
        """
        result = await self.call(prompt, schema=schema, temperature=temperature)
        if result is None:
            return None
        # Try to parse JSON from the response
        try:
            # Strip any markdown code fences
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return None

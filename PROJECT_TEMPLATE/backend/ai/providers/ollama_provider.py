"""Ollama provider implementation."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from ai.provider import AIProvider
from core.config import get_settings

logger = logging.getLogger(__name__)


class OllamaProvider(AIProvider):
    """Ollama local LLM provider."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model

    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate chat completion."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False, **kwargs},
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return {
                "content": data.get("message", {}).get("content", ""),
                "model": self.model,
                "usage": data.get("usage", {}),
            }

    async def validate_credentials(self) -> bool:
        """Verify Ollama is running."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama validation failed: {e}")
            return False

    async def health_check(self) -> bool:
        """Check provider availability."""
        return await self.validate_credentials()

    def get_supported_models(self) -> List[str]:
        """Return available models."""
        return ["llama3.2", "llama3.1", "mistral", "codellama"]
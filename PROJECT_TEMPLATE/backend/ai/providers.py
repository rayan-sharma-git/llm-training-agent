"""AI provider implementations."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from .base import AIProvider
from core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
        self._models: Optional[List[str]] = None
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response using OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": kwargs.get("model", "gpt-4o-mini"),
                    "messages": messages,
                    "temperature": kwargs.get("temperature", 0.7),
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate structured response."""
        schema_prompt = f"Return valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\n"
        full_prompt = schema_prompt + prompt
        response = await self.generate(full_prompt, system_prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse structured response"}
    
    def get_available_models(self) -> List[str]:
        """Get available models."""
        return ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"]
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        return bool(self.api_key)


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
        self._models: Optional[List[str]] = None
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response using Anthropic API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": kwargs.get("model", "claude-3-haiku-20240307"),
                    "max_tokens": kwargs.get("max_tokens", 4096),
                    "system": system_prompt or "",
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate structured response."""
        schema_prompt = f"Return valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\n"
        full_prompt = schema_prompt + prompt
        response = await self.generate(full_prompt, system_prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse structured response"}
    
    def get_available_models(self) -> List[str]:
        """Get available models."""
        return ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        return bool(self.api_key)


class OllamaProvider(AIProvider):
    """Ollama local provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._models: Optional[List[str]] = None
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate response using Ollama API."""
        model = kwargs.get("model", "llama3.2")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "system": system_prompt or "",
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["response"]
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any], system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate structured response."""
        schema_prompt = f"Return valid JSON matching this schema:\n{json.dumps(schema, indent=2)}\n\n"
        full_prompt = schema_prompt + prompt
        response = await self.generate(full_prompt, system_prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"error": "Failed to parse structured response", "raw": response}
    
    def get_available_models(self) -> List[str]:
        """Get available models."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self._fetch_models())
            return response
        except Exception:
            return ["llama3.2"]
    
    async def _fetch_models(self) -> List[str]:
        """Fetch models from Ollama."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/tags", timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    
    def is_available(self) -> bool:
        """Check if provider is available."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(self._check_health())
            return response
        except Exception:
            return False
    
    async def _check_health(self) -> bool:
        """Check Ollama health."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception:
            return False


def get_provider(provider_name: str) -> AIProvider:
    """Get AI provider instance by name."""
    settings = get_settings()
    
    if provider_name == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return OpenAIProvider(api_key=settings.openai_api_key)
    
    elif provider_name == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        return AnthropicProvider(api_key=settings.anthropic_api_key)
    
    elif provider_name == "ollama":
        return OllamaProvider(base_url=settings.ollama_base_url)
    
    else:
        raise ValueError(f"Unknown provider: {provider_name}")
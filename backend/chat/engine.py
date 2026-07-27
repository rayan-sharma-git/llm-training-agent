"""Chat engine for conversational interface."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from models.schemas import ChatMessage, ProjectContext
from ai.provider import AIProvider
from core.errors import ProviderError

logger = logging.getLogger(__name__)


class ChatEngine:
    """Handles chat interactions with project context."""

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def generate_response(self, session_id: str, message: str, context: ProjectContext, history: List[ChatMessage]) -> Dict[str, str]:
        """Generate AI response with project context."""
        try:
            system_prompt = f"You are an ML engineering assistant analyzing project: {context.project_name}. Use the provided context to answer questions."
            context_summary = f"Framework: {context.detected_framework}, Model: {context.base_model}, Datasets: {len(context.dataset_paths)}"
            messages = [{"role": "system", "content": system_prompt + "\nContext: " + context_summary}]
            for msg in history[-10:]:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": message})
            result = await self.provider.chat_completion(messages)
            return {"response": result.get("content", ""), "model": result.get("model", "unknown")}
        except Exception as e:
            logger.error(f"Chat response generation failed: {e}")
            raise ProviderError(f"Chat failed: {e}", "unknown")
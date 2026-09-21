"""Chat engine for conversational interface."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from models.schemas import ProjectContext, EngineeringReport, Recommendation, ChatMessage
from ai.providers import get_provider
from core.config import get_settings, get_active_provider
from core.errors import AppError

logger = logging.getLogger(__name__)


class ChatEngine:
    """Manages conversational interactions about the project."""

    def __init__(self, provider_name: Optional[str] = None):
        # Explicit provider name (e.g. from the request) wins; otherwise use
        # the runtime-selected provider, falling back to the configured default.
        self.provider_name = provider_name or get_active_provider() or get_settings().default_provider
        self._provider = None

    @property
    def provider(self):
        """Lazily instantiate the AI provider."""
        if self._provider is None:
            self._provider = get_provider(self.provider_name)
        return self._provider

    async def ask(
        self,
        context: ProjectContext,
        report: Optional[EngineeringReport],
        recommendations: List[Recommendation],
        question: str,
        chat_history: Optional[List[ChatMessage]] = None,
    ) -> Dict[str, Any]:
        """Answer a user question about the project using the configured AI provider."""
        logger.info(f"Chat question: {question}")

        messages: List[Dict[str, str]] = []

        # Build system prompt
        if report:
            system_prompt = (
                "You are an ML engineering assistant. Answer questions about the "
                f"user's fine-tuning project based on the provided analysis context.\n\n"
                f"Project: {context.project_name}\n"
                f"Framework: {context.detected_framework}\n"
                f"Health Score: {report.project_health_score:.0%}\n"
                f"Readiness Score: {report.training_readiness_score:.0%}\n"
            )
        else:
            system_prompt = (
                "You are an ML engineering assistant. Answer questions about the "
                f"user's fine-tuning project. Project: {context.project_name}"
            )

        # Add chat history
        if chat_history:
            for msg in chat_history:
                messages.append({"role": msg.role, "content": msg.content})

        # Add top recommendations as context (in user message)
        rec_context = ""
        if recommendations:
            rec_context = "\n\nTop Recommendations:\n"
            for rec in recommendations[:3]:
                rec_context += f"- {rec.title}: {rec.description}\n"

        # Build the user message with context
        user_message = (
            f"Context: Project '{context.project_name}', Framework: {context.detected_framework}\n"
            f"{rec_context}"
            f"\nQuestion: {question}\n\nAnswer:"
        )
        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.provider.chat_completion(messages, system=system_prompt)
            return {
                "assistantResponse": response["content"],
                "references": ["project_context", "analysis_results"],
                "confidence": "medium",
                "model": response.get("model", self.provider_name),
            }
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise AppError(
                message="Failed to generate chat response. The AI provider may be unavailable.",
                error_code="PROVIDER_UNAVAILABLE",
                details={"provider": self.provider_name, "error": str(e)},
            )

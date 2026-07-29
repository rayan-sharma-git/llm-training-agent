"""Chat engine for conversational interface."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from models.schemas import ProjectContext, EngineeringReport, Recommendation
from ai.providers import get_provider
from core.config import get_settings


class ChatEngine:
    """Manages conversational interactions about the project."""
    
    def __init__(self):
        self.provider = get_provider(get_settings().default_provider)
    
    async def ask(self, context: ProjectContext, report: Optional[EngineeringReport], recommendations: List[Recommendation], question: str) -> Dict[str, Any]:
        """Answer user question about the project."""
        logging.info(f"Chat question: {question}")
        
        # Build context for the prompt
        context_str = f"Project: {context.project_name}\nFramework: {context.detected_framework}\n"
        
        if report:
            context_str += f"\nHealth Score: {report.project_health_score:.0%}\n"
            context_str += f"Readiness Score: {report.training_readiness_score:.0%}\n"
        
        if recommendations:
            context_str += f"\nTop Recommendations:\n"
            for rec in recommendations[:3]:
                context_str += f"- {rec.title}: {rec.description}\n"
        
        system_prompt = "You are an ML engineering assistant. Answer questions about the user's fine-tuning project based on the provided analysis context."
        
        prompt = f"{context_str}\n\nQuestion: {question}\n\nAnswer:"
        
        try:
            response = await self.provider.generate(prompt, system_prompt=system_prompt)
            return {
                "assistantResponse": response,
                "references": ["project_context", "analysis_results"],
                "confidence": "medium",
            }
        except Exception as e:
            logging.error(f"Chat failed: {e}")
            return {
                "assistantResponse": f"Unable to generate response: {str(e)}",
                "references": [],
                "confidence": "low",
            }
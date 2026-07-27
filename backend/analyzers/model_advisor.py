"""Base model advisor for LLM selection."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from analyzers.base import Analyzer
from models.schemas import ModelAnalysisResult
from core.errors import AnalysisError

logger = logging.getLogger(__name__)


class ModelAdvisor(Analyzer):
    """Advises on base model selection and alternatives."""

    KNOWN_MODELS = {
        "tinyllama": {"params": "1.1B", "vram": "~4GB", "reasoning": "medium", "coding": "medium", "multilingual": "low"},
        "llama": {"params": "7B", "vram": "~16GB", "reasoning": "high", "coding": "high", "multilingual": "high"},
        "gemma": {"params": "2B", "vram": "~6GB", "reasoning": "medium", "coding": "medium", "multilingual": "high"},
        "mistral": {"params": "7B", "vram": "~16GB", "reasoning": "high", "coding": "high", "multilingual": "high"},
        "qwen": {"params": "7B", "vram": "~16GB", "reasoning": "high", "coding": "high", "multilingual": "very_high"},
    }

    async def analyze(self, context, **kwargs) -> Dict[str, Any]:
        """Analyze model suitability."""
        try:
            model = kwargs.get("model") or context.base_model or "unknown"
            model_info = self.KNOWN_MODELS.get(model.lower(), {
                "params": "unknown", "vram": "unknown", "reasoning": "medium", "coding": "medium", "multilingual": "medium"
            })
            recommendations = []
            known_models = list(self.KNOWN_MODELS.keys())
            if model.lower() not in self.KNOWN_MODELS:
                recommendations.append(f"Unknown model {model}. Consider: {', '.join(known_models)}")
            return ModelAnalysisResult(
                selected_model=model,
                parameter_count=model_info["params"],
                context_length=4096,
                estimated_vram=model_info["vram"],
                reasoning_capability=model_info["reasoning"],
                coding_capability=model_info["coding"],
                multilingual_capability=model_info["multilingual"],
                instruction_following_capability="medium",
                speed_score="medium",
                memory_efficiency="medium",
                strengths=["Good for fine-tuning"],
                weaknesses=["Context length may be limited"],
                recommended_alternatives=recommendations,
                confidence="medium",
            ).model_dump()
        except Exception as e:
            logger.error(f"Model analysis failed: {e}")
            raise AnalysisError(f"Model analysis failed: {e}")
"""Model selection advisor."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from models.schemas import ProjectContext, ModelAnalysisResult


class ModelAdvisor:
    """Advises on base model selection."""
    
    async def analyze(self, context: ProjectContext) -> ModelAnalysisResult:
        """Analyze selected model suitability."""
        logging.info("Analyzing model")
        
        # Stub implementation
        return ModelAnalysisResult(
            selected_model=context.base_model or "unknown",
            parameter_count="7B",
            context_length=4096,
            estimated_vram="8GB",
            reasoning_capability="medium",
            coding_capability="medium",
            multilingual_capability="medium",
            instruction_following_capability="medium",
            speed_score="medium",
            memory_efficiency="medium",
            strengths=["Good balance of speed and quality"],
            weaknesses=["Limited context length"],
            recommended_alternatives=["Consider larger model for complex reasoning"],
            confidence="medium",
        )
"""Recommendation generation engine."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

from models.schemas import Recommendation, Severity, Confidence

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Merges analyzer outputs into prioritized recommendations."""

    async def generate(self, context, dataset_result, prompt_result, hp_result, model_result, cost_result, prediction_result) -> List[Dict[str, Any]]:
        """Generate recommendations from all analyzer results."""
        recommendations = []

        # Dataset recommendations
        if dataset_result.get("duplicate_percentage", 0) > 1.0:
            recommendations.append(self._create_rec(
                category="dataset",
                title="Reduce duplicate samples",
                description=f"Duplicate rate is {dataset_result['duplicate_percentage']}%",
                evidence=f"Dataset analysis found {dataset_result['duplicate_percentage']}% duplicates",
                severity="high" if dataset_result['duplicate_percentage'] > 5 else "medium",
                confidence=dataset_result.get("confidence", "medium"),
                benefit="Improved training quality and reduced compute waste",
            ))

        # Hyperparameter recommendations
        if hp_result.get("learning_rate", 0) > 1e-3:
            recommendations.append(self._create_rec(
                category="hyperparameter",
                title="Reduce learning rate",
                description=f"Learning rate {hp_result['learning_rate']} is above recommended threshold",
                evidence="High learning rates commonly cause divergence in fine-tuning",
                severity="high",
                confidence="high",
                benefit="More stable training and better convergence",
            ))

        # Model recommendations
        if model_result.get("selected_model") == "unknown":
            recommendations.append(self._create_rec(
                category="model",
                title="Select a known base model",
                description="Unknown model detected - compatibility may be uncertain",
                evidence="Model analysis could not identify model capabilities",
                severity="medium",
                confidence="medium",
                benefit="Better predictability of training behavior",
            ))

        # Cost recommendations
        if cost_result.get("estimated_gpu_hours", 0) > 10:
            recommendations.append(self._create_rec(
                category="cost",
                title="Optimize training configuration to reduce cost",
                description="Estimated training time exceeds 10 GPU hours",
                evidence="Cost estimate based on current configuration",
                severity="low",
                confidence="medium",
                benefit="Reduced compute cost and faster experimentation",
            ))

        # Prediction recommendations
        if prediction_result.get("hallucination_risk") == "high":
            recommendations.append(self._create_rec(
                category="prediction",
                title="Address high hallucination risk",
                description="Model may produce unreliable outputs after fine-tuning",
                evidence="Prediction based on dataset quality and model capabilities",
                severity="high",
                confidence="medium",
                benefit="More reliable model outputs in production",
            ))

        return [r.model_dump() for r in recommendations]

    def _create_rec(self, category: str, title: str, description: str, evidence: str, severity: str, confidence: str, benefit: str) -> Recommendation:
        """Create a recommendation object."""
        return Recommendation(
            recommendation_id=str(uuid.uuid4()),
            category=category,
            title=title,
            description=description,
            reasoning=f"Analysis detected this issue based on {evidence}",
            evidence=evidence,
            severity=severity,
            confidence=confidence,
            estimated_benefit=benefit,
            implementation_difficulty="moderate",
            estimated_engineering_time="1-2 hours",
            affected_files=[],
            suggested_actions=[title],
            references=[],
        )
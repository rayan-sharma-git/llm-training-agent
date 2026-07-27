"""Engineering report generator."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from models.schemas import EngineeringReport, Recommendation

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive engineering reports."""

    def generate(self, context, dataset_result, prompt_result, hp_result, model_result, cost_result, prediction_result, recommendations) -> Dict[str, Any]:
        """Generate engineering report from analysis results."""
        try:
            health_score = self._compute_health_score(dataset_result, hp_result, model_result)
            readiness_score = self._compute_readiness_score(dataset_result, hp_result, model_result, prediction_result)
            rec_list = [Recommendation(**r) if isinstance(r, dict) else r for r in recommendations]
            rec_list.sort(key=lambda r: {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}.get(r.severity, 2))
            report = EngineeringReport(
                executive_summary=f"Analysis of {context.project_name} completed with health score {health_score:.2f}",
                project_health_score=health_score,
                training_readiness_score=readiness_score,
                dataset_summary={"quality_score": dataset_result.get("quality_score"), "findings": dataset_result.get("findings", [])},
                prompt_summary={"clarity_score": prompt_result.get("clarity_score"), "issues": prompt_result.get("detected_issues", [])},
                hyperparameter_summary={"learning_rate": hp_result.get("learning_rate"), "efficiency_score": hp_result.get("efficiency_score")},
                model_summary={"model": model_result.get("selected_model"), "vram": model_result.get("estimated_vram")},
                prediction_summary={"hallucination_risk": prediction_result.get("hallucination_risk")},
                cost_summary={"gpu_hours": cost_result.get("estimated_gpu_hours"), "training_time": cost_result.get("estimated_training_time")},
                prioritized_recommendations=rec_list,
                action_plan=[r.title for r in rec_list[:5]],
            )
            return report.model_dump()
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise

    def _compute_health_score(self, dataset_result, hp_result, model_result) -> float:
        score = 0.8
        if dataset_result.get("quality_score", 0) < 0.8:
            score -= 0.2
        if hp_result.get("efficiency_score", 0) < 0.8:
            score -= 0.15
        if model_result.get("selected_model") == "unknown":
            score -= 0.1
        return max(0.0, min(1.0, score))

    def _compute_readiness_score(self, dataset_result, hp_result, model_result, prediction_result) -> float:
        score = self._compute_health_score(dataset_result, hp_result, model_result)
        if prediction_result.get("hallucination_risk") == "high":
            score -= 0.1
        return max(0.0, min(1.0, score))
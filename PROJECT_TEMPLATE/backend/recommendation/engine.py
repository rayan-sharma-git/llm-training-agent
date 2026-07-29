"""Recommendation generation engine."""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional
from models.schemas import (
    ProjectContext,
    DatasetAnalysisResult,
    PromptAnalysisResult,
    HyperparameterAnalysisResult,
    ModelAnalysisResult,
    CostEstimate,
    PredictionResult,
    Recommendation,
    EngineeringReport,
)


class RecommendationEngine:
    """Generates prioritized recommendations from analysis results."""
    
    async def generate(self, context: ProjectContext, dataset_result: DatasetAnalysisResult, prompt_result: PromptAnalysisResult, hp_result: HyperparameterAnalysisResult, model_result: ModelAnalysisResult, cost_result: CostEstimate, prediction_result: PredictionResult) -> List[Recommendation]:
        """Generate recommendations."""
        logging.info("Generating recommendations")
        
        recommendations = []
        
        # Example: dataset recommendation
        if dataset_result.duplicate_percentage > 5.0:
            recommendations.append(self._create_recommendation(
                category="dataset",
                title="Remove duplicate samples",
                description=f"Dataset contains {dataset_result.duplicate_percentage}% duplicates",
                reasoning="Duplicates reduce training efficiency",
                evidence=f"Duplicate percentage: {dataset_result.duplicate_percentage}%",
                severity="high",
                confidence="high",
                estimated_benefit="10-20% faster training",
                implementation_difficulty="easy",
                estimated_engineering_time="1-2 hours",
                affected_files=context.dataset_paths,
                suggested_actions=["Run deduplication script", "Verify dataset integrity"],
            ))
        
        # Example: hyperparameter recommendation
        if hp_result.learning_rate and hp_result.learning_rate > 1e-3:
            recommendations.append(self._create_recommendation(
                category="hyperparameter",
                title="Reduce learning rate",
                description=f"Learning rate {hp_result.learning_rate} may be too high",
                reasoning="High learning rates can cause training instability",
                evidence=f"Current learning rate: {hp_result.learning_rate}",
                severity="medium",
                confidence="medium",
                estimated_benefit="More stable training",
                implementation_difficulty="easy",
                estimated_engineering_time="30 minutes",
                affected_files=[],
                suggested_actions=["Reduce learning rate by 10x", "Add learning rate scheduler"],
            ))
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        recommendations.sort(key=lambda r: severity_order.get(r.severity, 5))
        
        return recommendations
    
    def _create_recommendation(self, **kwargs) -> Recommendation:
        """Helper to create recommendation with UUID."""
        return Recommendation(recommendation_id=str(uuid.uuid4()), **kwargs)
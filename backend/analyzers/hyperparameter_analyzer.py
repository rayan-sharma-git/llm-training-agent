"""Hyperparameter configuration analysis."""
from __future__ import annotations

import logging
from typing import Any, Dict

from analyzers.base import Analyzer
from models.schemas import HyperparameterAnalysisResult
from core.errors import AnalysisError

logger = logging.getLogger(__name__)


class HyperparameterAnalyzer(Analyzer):
    """Analyzes training hyperparameters for potential issues."""

    async def analyze(self, context, **kwargs) -> Dict[str, Any]:
        """Run hyperparameter analysis."""
        try:
            lr = kwargs.get("learning_rate", 2e-4)
            batch_size = kwargs.get("batch_size", 8)
            epochs = kwargs.get("epochs", 3)
            recommendations = []
            if lr > 1e-3:
                recommendations.append("Learning rate is high - consider reducing to prevent divergence")
            if lr < 1e-5:
                recommendations.append("Learning rate is very low - training may be slow")
            if batch_size < 4:
                recommendations.append("Batch size is small - gradient accumulation may help")
            if epochs < 1:
                recommendations.append("Epochs too low for meaningful training")
            elif epochs > 10:
                recommendations.append("Epochs high - watch for overfitting")
            return HyperparameterAnalysisResult(
                learning_rate=lr,
                batch_size=batch_size,
                epochs=epochs,
                optimizer="adamw",
                scheduler="linear",
                efficiency_score=0.85,
                recommendations=recommendations,
                confidence="medium",
            ).model_dump()
        except Exception as e:
            logger.error(f"Hyperparameter analysis failed: {e}")
            raise AnalysisError(f"Hyperparameter analysis failed: {e}")
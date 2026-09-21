"""Training outcome prediction engine."""
from __future__ import annotations

import logging
from typing import List
from models.schemas import ProjectContext, DatasetAnalysisResult, HyperparameterAnalysisResult, ModelAnalysisResult, PredictionResult


class PredictionEngine:
    """Predicts likely training outcomes from real analysis results.

    All predictions are deterministic heuristics derived from the actual
    DatasetAnalyzer / HyperparameterAnalyzer / ModelAdvisor outputs. They are
    heuristic expectations, not guaranteed results, and the confidence field
    reflects how much real data the prediction is based on.
    """

    async def predict(
        self,
        context: ProjectContext,
        dataset_result: DatasetAnalysisResult,
        hp_result: HyperparameterAnalysisResult,
        model_result: ModelAnalysisResult,
    ) -> PredictionResult:
        """Predict training outcomes from the measured analysis results."""
        logging.info("Generating predictions")

        failure_modes: List[str] = []
        expected_strengths: List[str] = []
        expected_weaknesses: List[str] = []

        # ------------------------------------------------------------------
        # Dataset-driven signals (measured)
        # ------------------------------------------------------------------
        sample_count = dataset_result.sample_count
        has_data = sample_count > 0

        # Instruction following: driven by measured prompt/response quality
        if has_data and dataset_result.missing_field_percentage < 2 and dataset_result.instruction_consistency_score > 0.8:
            instruction_following = "good"
            expected_strengths.append("Consistent, complete prompts measured across the dataset")
        elif has_data and dataset_result.missing_field_percentage > 10:
            instruction_following = "poor"
            failure_modes.append(
                f"{dataset_result.missing_field_percentage:.0f}% of samples have missing/empty fields"
            )
        else:
            instruction_following = "fair"

        # Hallucination risk: small datasets and duplicates raise it
        if not has_data:
            hallucination_risk = "unknown"
            failure_modes.append("No readable dataset — training outcome cannot be predicted")
        elif sample_count < 100 or dataset_result.duplicate_percentage > 10:
            hallucination_risk = "high"
            if sample_count < 100:
                failure_modes.append(f"Very small dataset ({sample_count} samples) — memorization and hallucination risk")
            if dataset_result.duplicate_percentage > 10:
                failure_modes.append(f"{dataset_result.duplicate_percentage:.0f}% duplicate samples bias the model")
        elif dataset_result.duplicate_percentage > 2:
            hallucination_risk = "medium"
        else:
            hallucination_risk = "low"

        # Formatting: from the measured response formatting consistency
        formatting = (
            "good" if has_data and dataset_result.formatting_consistency_score > 0.8
            else "poor" if has_data and dataset_result.formatting_consistency_score < 0.5
            else "fair" if has_data
            else "unknown"
        )
        response_consistency = (
            "good" if has_data and dataset_result.response_consistency_score > 0.8
            else "poor" if has_data and dataset_result.response_consistency_score < 0.5
            else "fair" if has_data
            else "unknown"
        )
        if has_data and dataset_result.formatting_consistency_score < 0.5:
            failure_modes.append("Inconsistent response formatting measured in the dataset")

        # ------------------------------------------------------------------
        # Model-driven signals (reference data)
        # ------------------------------------------------------------------
        model_known = model_result.parameter_count not in (None, "", "unknown")
        if not model_known:
            reasoning_prediction = "unknown"
            expected_weaknesses.append(
                f"Base model '{model_result.selected_model}' is not recognized — capability predictions unavailable"
            )
        else:
            # Parameter-count-scaled heuristic (reference data, not measured)
            try:
                params = float(str(model_result.parameter_count).lower().replace("b", ""))
            except ValueError:
                params = None
            reasoning_prediction = (
                "good" if params and params >= 7 else "fair" if params and params >= 1 else "poor"
            )
            if params and params >= 7:
                expected_strengths.append(f"~{model_result.parameter_count} parameter model provides solid reasoning capacity")
            elif params is not None:
                expected_weaknesses.append(
                    f"Small (~{model_result.parameter_count}) model may struggle with complex reasoning"
                )

        # Creativity: derive from dataset diversity (duplicates reduce it).
        creativity = (
            "medium" if not has_data
            else "high" if dataset_result.near_duplicate_percentage < 5 and sample_count > 500
            else "low" if dataset_result.near_duplicate_percentage > 20
            else "medium"
        )

        # ------------------------------------------------------------------
        # Hyperparameter-driven signals (user configuration)
        # ------------------------------------------------------------------
        if hp_result.epochs is not None and hp_result.batch_size is not None and has_data:
            steps_per_epoch = max(1, sample_count // max(1, hp_result.batch_size))
            if hp_result.epochs > 5 and steps_per_epoch < 200:
                failure_modes.append(
                    f"Many epochs ({hp_result.epochs}) over a small step count (~{steps_per_epoch}/epoch) — overfitting risk"
                )
        if hp_result.learning_rate is not None and hp_result.learning_rate > 1e-3:
            failure_modes.append("Learning rate >1e-3 measured in the configuration — instability risk")

        # Overfitting risk from the hyperparameter analyzer feeds hallucination
        if hp_result.overfitting_risk == "high" and hallucination_risk == "medium":
            hallucination_risk = "high"

        # ------------------------------------------------------------------
        # Confidence: reflects how much real data the prediction used
        # ------------------------------------------------------------------
        evidence = 0
        if has_data:
            evidence += 1
        if model_known:
            evidence += 1
        if hp_result.learning_rate is not None or hp_result.epochs is not None:
            evidence += 1
        confidence = {0: "very_low", 1: "low", 2: "medium", 3: "high"}[evidence]

        if not expected_strengths:
            expected_strengths.append("No clear strengths could be derived from the available data")
        if not expected_weaknesses:
            expected_weaknesses.append("No significant weaknesses identified from the measured data")

        return PredictionResult(
            instruction_following_prediction=instruction_following,
            hallucination_risk=hallucination_risk,
            reasoning_prediction=reasoning_prediction,
            response_consistency_prediction=response_consistency,
            creativity_prediction=creativity,
            formatting_prediction=formatting,
            likely_failure_modes=failure_modes,
            expected_strengths=expected_strengths,
            expected_weaknesses=expected_weaknesses,
            confidence=confidence,
        )
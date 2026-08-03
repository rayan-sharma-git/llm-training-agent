"""FastAPI route handlers."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from models.schemas import (
    ProjectContext,
    DatasetAnalysisResult,
    PromptAnalysisResult,
    HyperparameterAnalysisResult,
    ModelAnalysisResult,
    PredictionResult,
    CostEstimate,
    Recommendation,
    EngineeringReport,
    ApiError,
)
from scanner.scanner import ProjectScanner
from scanner.context_builder import ContextBuilder
from analyzers.dataset_analyzer import DatasetAnalyzer
from analyzers.prompt_analyzer import PromptAnalyzer
from analyzers.hyperparameter_analyzer import HyperparameterAnalyzer
from analyzers.model_advisor import ModelAdvisor
from analyzers.cost_estimator import CostEstimator
from prediction.engine import PredictionEngine
from recommendation.engine import RecommendationEngine
from reports.generator import ReportGenerator
from core.errors import AppError

logger = logging.getLogger(__name__)
router = APIRouter()

_analyzer_cache: Dict[str, Any] = {}


def _get_analyzer(name: str):
    if name not in _analyzer_cache:
        if name == "dataset":
            _analyzer_cache[name] = DatasetAnalyzer()
        elif name == "prompt":
            _analyzer_cache[name] = PromptAnalyzer()
        elif name == "hyperparameters":
            _analyzer_cache[name] = HyperparameterAnalyzer()
        elif name == "model":
            _analyzer_cache[name] = ModelAdvisor()
        elif name == "cost":
            _analyzer_cache[name] = CostEstimator()
    return _analyzer_cache[name]


@router.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@router.post("/project/analyze", response_model=Dict[str, Any])
async def analyze_project(request: Dict[str, str]):
    try:
        project_path = request.get("projectPath")
        if not project_path:
            raise HTTPException(status_code=400, detail="projectPath is required")
        scanner = ProjectScanner(project_path)
        scan_result = scanner.scan()
        context_builder = ContextBuilder()
        context = context_builder.build(scan_result)
        dataset_analyzer = _get_analyzer("dataset")
        prompt_analyzer = _get_analyzer("prompt")
        hp_analyzer = _get_analyzer("hyperparameters")
        model_advisor = _get_analyzer("model")
        cost_estimator = _get_analyzer("cost")
        prediction_engine = PredictionEngine()
        rec_engine = RecommendationEngine()
        report_gen = ReportGenerator()
        dataset_result = await dataset_analyzer.analyze(context)
        prompt_result = await prompt_analyzer.analyze(context)
        hp_result = await hp_analyzer.analyze(context)
        model_result = await model_advisor.analyze(context)
        cost_result = await cost_estimator.analyze(context)
        prediction_result = await prediction_engine.predict(context, dataset_result, hp_result, model_result)
        recommendations = await rec_engine.generate(context, dataset_result, prompt_result, hp_result, model_result, cost_result, prediction_result)
        report = report_gen.generate(context, dataset_result, prompt_result, hp_result, model_result, cost_result, prediction_result, recommendations)
        return {"project": context.model_dump(), "report": report}
    except AppError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.get("/project/context")
async def get_project_context():
    return {"message": "No project context available"}


@router.post("/project/refresh")
async def refresh_project():
    return {"message": "Refresh not yet implemented"}


@router.post("/dataset/analyze")
async def analyze_dataset(request: Dict[str, Any]):
    try:
        dataset_path = request.get("datasetPath")
        if not dataset_path:
            raise HTTPException(status_code=400, detail="datasetPath is required")
        # Simplified - would need real context/repository in production
        analyzer = DatasetAnalyzer()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path=dataset_path)
        result = await analyzer.analyze(dummy_context, dataset_path=dataset_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/prompt/analyze")
async def analyze_prompt(request: Dict[str, Any]):
    try:
        template = request.get("promptTemplate")
        if not template:
            raise HTTPException(status_code=400, detail="promptTemplate is required")
        analyzer = PromptAnalyzer()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path="")
        dummy_context.prompt_templates = [template]
        result = await analyzer.analyze(dummy_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/hyperparameters/analyze")
async def analyze_hyperparameters(request: Dict[str, Any]):
    try:
        analyzer = HyperparameterAnalyzer()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path="")
        result = await analyzer.analyze(dummy_context, **request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/model/analyze")
async def analyze_model(request: Dict[str, Any]):
    try:
        advisor = ModelAdvisor()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path="")
        result = await advisor.analyze(dummy_context, **request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/predict/training")
async def predict_training(request: Dict[str, Any]):
    try:
        engine = PredictionEngine()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path="")
        result = await engine.predict(dummy_context, {}, {}, {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/cost/estimate")
async def estimate_cost(request: Dict[str, Any]):
    try:
        estimator = CostEstimator()
        from models.schemas import ProjectContext
        dummy_context = ProjectContext(project_name="temp", project_path="")
        result = await estimator.analyze(dummy_context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.get("/recommendations")
async def get_recommendations():
    return {"recommendations": []}


@router.post("/recommendations/refresh")
async def refresh_recommendations():
    return {"recommendations": []}


@router.get("/report")
async def get_report():
    # In a full implementation this would retrieve the latest stored report.
    # For production readiness, return a clear no-data response.
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "No report available"})


@router.post("/chat/message")
async def chat_message(request: Dict[str, Any]):
    try:
        message = request.get("message")
        if not message:
            raise HTTPException(status_code=400, detail="message is required")
        # TODO: integrate with configured AI provider via chat service.
        if not message.strip():
            raise HTTPException(status_code=422, detail="message must not be empty")
        return {
            "assistantResponse": "Backend received the message but AI integration is pending.",
            "references": [],
            "confidence": "low",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "CHAT_FAILED", "message": str(e)})


@router.get("/chat/history")
async def get_chat_history():
    return {"messages": []}


@router.delete("/chat/history")
async def delete_chat_history():
    return {"status": "cleared"}


@router.get("/experiments")
async def list_experiments():
    return {"experiments": []}


@router.get("/providers")
async def list_providers():
    return {"providers": ["openai", "anthropic", "ollama"]}


@router.get("/config")
async def get_config():
    from core.config import get_settings
    settings = get_settings()
    return {"default_provider": settings.default_provider.value}
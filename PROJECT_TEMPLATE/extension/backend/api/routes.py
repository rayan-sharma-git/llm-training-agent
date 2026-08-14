"""FastAPI route handlers."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
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
from chat.engine import ChatEngine
from core.errors import AppError, AnalysisError
from core.config import get_settings, reload_settings, get_active_provider, get_active_model
from core import runtime_config
from ai.providers import list_providers, get_models, get_provider

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers for safe typed-result reconstruction
# ---------------------------------------------------------------------------

def _safe_model(data: Dict[str, Any], model_cls: type, **defaults) -> Any:
    """Safely construct a Pydantic model from a results dict.

    If *data* is the result of a successful analyzer, its keys will match the
    model fields and construction succeeds.  If *data* is a fallback error
    dict (missing required fields or containing extra ``error`` key), we
    fall back to *defaults*.
    """
    try:
        return model_cls(**{k: v for k, v in data.items() if k in model_cls.model_fields})
    except Exception:
        return model_cls(**defaults)


def _default_dataset_result() -> DatasetAnalysisResult:
    return DatasetAnalysisResult(
        dataset_name="unknown", sample_count=0, token_count=0,
        average_prompt_length=0, average_response_length=0,
        duplicate_percentage=0, near_duplicate_percentage=0,
        missing_field_percentage=0, formatting_consistency_score=0,
        language_consistency_score=0, instruction_consistency_score=0,
        response_consistency_score=0, quality_score=0, confidence="low",
    )


def _default_prompt_result() -> PromptAnalysisResult:
    return PromptAnalysisResult(
        template_name="unknown", ambiguity_score=0.5, clarity_score=0.5,
        formatting_score=0.5, instruction_quality_score=0.5,
        consistency_score=0.5, confidence="low",
    )


def _default_hp_result() -> HyperparameterAnalysisResult:
    return HyperparameterAnalysisResult(efficiency_score=0.5, confidence="low")


def _default_model_result() -> ModelAnalysisResult:
    return ModelAnalysisResult(
        selected_model="unknown", parameter_count="unknown",
        context_length=0, estimated_vram="unknown", confidence="low",
    )


def _default_cost_result() -> CostEstimate:
    return CostEstimate(
        estimated_training_time="unknown", estimated_gpu_hours=0.0,
        estimated_vram_usage="unknown", estimated_checkpoint_size="unknown",
        estimated_storage_requirement="unknown", confidence="low",
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@router.get("/health")
async def health():
    """Simple health endpoint - used by the extension to check backend availability."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Provider / configuration
# ---------------------------------------------------------------------------

class ProviderConfigRequest(BaseModel):
    provider: str
    model: str


class SaveConfigRequest(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    apiKey: Optional[str] = None
    baseUrl: Optional[str] = None


class TestConnectionRequest(BaseModel):
    provider: str
    model: Optional[str] = None
    apiKey: Optional[str] = None
    baseUrl: Optional[str] = None


@router.get("/providers")
async def get_providers():
    """Return all available AI providers and their supported models."""
    settings = get_settings()
    provider_info = list_providers()
    result = {}
    for name, info in provider_info.items():
        configured = True
        if info["requires_key"]:
            key_field = f"{name}_api_key" if name != "openai_compatible" else "openai_compatible_api_key"
            if name == "openai_compatible":
                configured = bool(runtime_config.get_api_key("openai_compatible") or settings.openai_compatible_api_key)
            else:
                configured = bool(runtime_config.get_api_key(name) or getattr(settings, key_field, None))
        result[name] = {
            "requiresKey": info["requires_key"],
            "models": info["models"],
            "description": info["description"],
            "configured": configured,
        }
    return {"providers": result}


@router.get("/provider/models")
async def get_provider_models(provider: str = "ollama"):
    """Get available models for the specified provider."""
    try:
        models = get_models(provider)
        return {"provider": provider, "models": models}
    except Exception as e:
        return {"provider": provider, "models": [], "error": str(e)}


@router.post("/provider/select")
async def select_provider(request: ProviderConfigRequest):
    """Select active AI provider and model (persists in runtime config)."""
    valid_providers = list_providers()
    if request.provider not in valid_providers:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{request.provider}'. Valid: {list(valid_providers.keys())}",
        )
    runtime_config.set_runtime_config("provider", request.provider)
    runtime_config.set_runtime_config("model", request.model)
    return {
        "provider": request.provider,
        "model": request.model,
        "message": f"Provider set to {request.provider}, model {request.model}.",
    }


@router.get("/config")
async def get_config():
    """Return current configuration."""
    settings = get_settings()
    provider = get_active_provider()
    model = get_active_model(provider)
    return {
        "default_provider": provider,
        "default_model": model,
        "ollama_base_url": runtime_config.get_runtime_config("ollama_base_url") or settings.ollama_base_url,
        "openai_compatible_base_url": runtime_config.get_runtime_config("openai_compatible_base_url") or settings.openai_compatible_base_url,
    }


@router.put("/config")
async def update_config(request: SaveConfigRequest):
    """Update configuration (provider, model, API keys, base URLs).

    API keys are stored in memory only (never written to disk).
    The extension sends them securely from VS Code SecretStorage.
    """
    updated: Dict[str, Any] = {}

    if request.provider:
        valid_providers = list_providers()
        if request.provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider '{request.provider}'. Valid: {list(valid_providers.keys())}",
            )
        runtime_config.set_runtime_config("provider", request.provider)
        updated["provider"] = request.provider

    if request.model:
        runtime_config.set_runtime_config("model", request.model)
        updated["model"] = request.model

    if request.apiKey:
        provider = request.provider or get_active_provider()
        runtime_config.set_api_key(provider, request.apiKey)
        updated["apiKey"] = "stored"

    if request.baseUrl:
        provider = request.provider or get_active_provider()
        if provider == "ollama":
            runtime_config.set_runtime_config("ollama_base_url", request.baseUrl)
            updated["ollama_base_url"] = request.baseUrl
        elif provider == "openai_compatible":
            runtime_config.set_runtime_config("openai_compatible_base_url", request.baseUrl)
            updated["openai_compatible_base_url"] = request.baseUrl

    return {"status": "updated", "changed": updated}


@router.delete("/config/key")
async def remove_api_key(provider: str):
    """Remove the in-memory API key for a provider."""
    runtime_config.remove_api_key(provider)
    return {"status": "removed", "provider": provider}


@router.post("/provider/test")
async def test_connection(request: TestConnectionRequest):
    """Test the connection to an AI provider."""
    provider_name = request.provider.lower()
    valid_providers = list_providers()
    if provider_name not in valid_providers:
        return {
            "success": False,
            "message": f"Unknown provider '{provider_name}'.",
            "error": "UNKNOWN_PROVIDER",
        }

    if request.apiKey:
        runtime_config.set_api_key(provider_name, request.apiKey)
    if request.baseUrl:
        if provider_name == "ollama":
            runtime_config.set_runtime_config("ollama_base_url", request.baseUrl)
        elif provider_name == "openai_compatible":
            runtime_config.set_runtime_config("openai_compatible_base_url", request.baseUrl)
    if request.model:
        runtime_config.set_runtime_config("model", request.model)

    try:
        provider = get_provider(provider_name)
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "error": "PROVIDER_NOT_CONFIGURED",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to initialize provider: {str(e)}",
            "error": "PROVIDER_INIT_FAILED",
        }

    try:
        ok = await provider.validate_credentials()
        if ok:
            return {
                "success": True,
                "message": f"Connection to {provider_name} successful.",
                "provider": provider_name,
                "model": request.model or get_active_model(provider_name),
            }
        else:
            return {
                "success": False,
                "message": f"Connection to {provider_name} failed. Check your API key and model.",
                "error": "VALIDATION_FAILED",
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Connection test failed: {str(e)}",
            "error": "CONNECTION_FAILED",
        }


# ---------------------------------------------------------------------------
# Project analysis
# ---------------------------------------------------------------------------

@router.post("/project/analyze", response_model=Dict[str, Any])
async def analyze_project(request: Dict[str, str]):
    """Analyze an entire fine-tuning project.

    Request body:  {"projectPath": "/path/to/project"}
    """
    try:
        project_path = request.get("projectPath")
        if not project_path:
            raise HTTPException(
                status_code=400,
                detail="projectPath is required. Please ensure a workspace folder is open.",
            )

        from pathlib import Path
        if not Path(project_path).exists():
            raise HTTPException(
                status_code=404,
                detail=f"Project path does not exist: {project_path}",
            )

        logger.info(f"Starting project analysis: {project_path}")

        # Step 1: Scan project
        scanner = ProjectScanner(project_path)
        scan_result = scanner.scan()

        # Step 2: Build context
        context_builder = ContextBuilder()
        context = context_builder.build(scan_result)

        # Step 3: Run analyzers (with graceful degradation)
        results: Dict[str, Any] = {}

        dataset_analyzer = DatasetAnalyzer()
        prompt_analyzer = PromptAnalyzer()
        hp_analyzer = HyperparameterAnalyzer()
        model_advisor = ModelAdvisor()
        cost_estimator = CostEstimator()

        # Dataset analysis
        try:
            dataset_result_obj = await dataset_analyzer.analyze(context)
            results["dataset"] = dataset_result_obj.model_dump()
        except Exception as e:
            logger.error(f"DatasetAnalyzer failed: {e}")
            results["dataset"] = {"error": str(e), "quality_score": 0.0, "confidence": "low"}

        # Prompt analysis
        try:
            prompt_result_obj = await prompt_analyzer.analyze(context)
            results["prompt"] = prompt_result_obj.model_dump()
        except Exception as e:
            logger.error(f"PromptAnalyzer failed: {e}")
            results["prompt"] = {"error": str(e), "clarity_score": 0.5, "confidence": "low"}

        # Hyperparameter analysis
        try:
            hp_result_obj = await hp_analyzer.analyze(context)
            results["hyperparameters"] = hp_result_obj.model_dump()
        except Exception as e:
            logger.error(f"HyperparameterAnalyzer failed: {e}")
            results["hyperparameters"] = {"error": str(e), "efficiency_score": 0.5, "confidence": "low"}

        # Model analysis
        try:
            model_result_obj = await model_advisor.analyze(context)
            results["model"] = model_result_obj.model_dump()
        except Exception as e:
            logger.error(f"ModelAdvisor failed: {e}")
            results["model"] = {"error": str(e), "confidence": "low"}

        # Cost estimation
        try:
            cost_result_obj = await cost_estimator.analyze(context)
            results["cost"] = cost_result_obj.model_dump()
        except Exception as e:
            logger.error(f"CostEstimator failed: {e}")
            results["cost"] = {"error": str(e), "confidence": "low"}

        logger.info("All analyzers completed (with possible partial failures)")

        # Step 4: Predictions
        ds_result = _safe_model(results["dataset"], DatasetAnalysisResult, **_default_dataset_result().__dict__)
        hp_result = _safe_model(results["hyperparameters"], HyperparameterAnalysisResult, **_default_hp_result().__dict__)
        model_result = _safe_model(results["model"], ModelAnalysisResult, **_default_model_result().__dict__)

        try:
            prediction_engine = PredictionEngine()
            prediction_result = await prediction_engine.predict(
                context, ds_result, hp_result, model_result
            )
        except Exception as e:
            logger.error(f"PredictionEngine failed: {e}")
            prediction_result = PredictionResult(
                instruction_following_prediction="unknown",
                hallucination_risk="unknown",
                confidence="low",
            )

        # Step 5: Recommendations
        prompt_result = _safe_model(results["prompt"], PromptAnalysisResult, **_default_prompt_result().__dict__)
        cost_result = _safe_model(results["cost"], CostEstimate, **_default_cost_result().__dict__)

        try:
            rec_engine = RecommendationEngine()
            recommendations = await rec_engine.generate(
                context, ds_result, prompt_result, hp_result, model_result,
                cost_result, prediction_result
            )
        except Exception as e:
            logger.error(f"RecommendationEngine failed: {e}")
            recommendations = []

        # Step 6: Report
        try:
            report_gen = ReportGenerator()
            report = report_gen.generate(
                context, ds_result, prompt_result, hp_result, model_result,
                cost_result, prediction_result, recommendations
            )
        except Exception as e:
            logger.error(f"ReportGenerator failed: {e}")
            report = EngineeringReport(
                executive_summary=f"Analysis of {context.project_name} completed with errors.",
                project_health_score=0.0,
                training_readiness_score=0.0,
                prioritized_recommendations=[],
                action_plan=["Fix backend errors and re-run analysis."],
            )

        return {"project": context.model_dump(), "report": report.model_dump()}

    except HTTPException:
        raise
    except AppError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "errorCode": "ANALYSIS_FAILED",
                "message": "Project analysis failed. See server logs for details.",
                "error": str(e),
            },
        )


@router.get("/project/context")
async def get_project_context():
    """Return the latest project context (stub - returns no data until persistence is wired)."""
    return {"message": "No project context available. Run /project/analyze first."}


@router.post("/project/refresh")
async def refresh_project():
    """Re-scan the project and rebuild context."""
    return {"message": "Refresh not yet implemented"}


# ---------------------------------------------------------------------------
# Individual analyzer endpoints
# ---------------------------------------------------------------------------

@router.post("/dataset/analyze")
async def analyze_dataset(request: Dict[str, Any]):
    """Analyze a single dataset file."""
    try:
        dataset_path = request.get("datasetPath")
        if not dataset_path:
            raise HTTPException(status_code=400, detail="datasetPath is required")

        from pathlib import Path
        if not Path(dataset_path).exists():
            raise HTTPException(status_code=404, detail=f"Dataset file not found: {dataset_path}")

        analyzer = DatasetAnalyzer()
        dummy_context = ProjectContext(
            project_name=Path(dataset_path).stem,
            project_path=str(Path(dataset_path).parent),
            dataset_paths=[dataset_path],
        )
        result = await analyzer.analyze(dummy_context, dataset_path=dataset_path)
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dataset analysis failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/prompt/analyze")
async def analyze_prompt(request: Dict[str, Any]):
    """Analyze a single prompt template."""
    try:
        template = request.get("promptTemplate")
        template_path = request.get("templatePath")
        if not template and not template_path:
            raise HTTPException(status_code=400, detail="promptTemplate or templatePath is required")

        analyzer = PromptAnalyzer()
        context = ProjectContext(project_name="temp", project_path="")
        if template_path:
            context.prompt_templates = [template_path]
        if template:
            context.prompt_templates = [template]
        result = await analyzer.analyze(context)
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prompt analysis failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/hyperparameters/analyze")
async def analyze_hyperparameters(request: Dict[str, Any]):
    """Analyze training hyperparameters from a config file or inline values."""
    try:
        config_path = request.get("configPath")
        analyzer = HyperparameterAnalyzer()
        context = ProjectContext(project_name="temp", project_path="")
        result = await analyzer.analyze(context, config_path=config_path, **{k: v for k, v in request.items() if k != "configPath"})
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hyperparameter analysis failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/model/analyze")
async def analyze_model(request: Dict[str, Any]):
    """Analyze model suitability."""
    try:
        model_name = request.get("modelName") or request.get("model")
        advisor = ModelAdvisor()
        context = ProjectContext(project_name="temp", project_path="")
        if model_name:
            context.base_model = model_name
        result = await advisor.analyze(context)
        return result.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model analysis failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ANALYSIS_FAILED", "message": str(e)})


@router.post("/predict/training")
async def predict_training(request: Dict[str, Any]):
    """Predict training outcomes."""
    try:
        context = ProjectContext(project_name="temp", project_path="")
        dataset_result = DatasetAnalysisResult(dataset_name="unknown", sample_count=0, token_count=0,
            average_prompt_length=0, average_response_length=0, duplicate_percentage=0,
            near_duplicate_percentage=0, missing_field_percentage=0,
            formatting_consistency_score=0.9, language_consistency_score=0.9,
            instruction_consistency_score=0.9, response_consistency_score=0.9,
            quality_score=0.85, confidence="medium")
        hp_result = HyperparameterAnalysisResult(efficiency_score=0.75, confidence="medium")
        model_result = ModelAnalysisResult(selected_model="unknown", parameter_count="unknown",
            context_length=4096, estimated_vram="unknown", confidence="medium")
        engine = PredictionEngine()
        result = await engine.predict(context, dataset_result, hp_result, model_result)
        return result.model_dump()
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "PREDICTION_FAILED", "message": str(e)})


@router.post("/cost/estimate")
async def estimate_cost(request: Dict[str, Any]):
    """Estimate training cost."""
    try:
        estimator = CostEstimator()
        context = ProjectContext(project_name="temp", project_path="")
        result = await estimator.analyze(context)
        return result.model_dump()
    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ESTIMATION_FAILED", "message": str(e)})


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

@router.post("/chat/message")
async def chat_message(request: Dict[str, Any]):
    """Send a message to the AI chat."""
    try:
        message = request.get("message")
        if not message or not message.strip():
            raise HTTPException(status_code=422, detail="message must not be empty")

        provider_name = request.get("provider")
        session_id = request.get("sessionId", "default")

        try:
            engine = ChatEngine(provider_name=provider_name)
            context = ProjectContext(project_name="current_project", project_path="")
            response = await engine.ask(context, None, [], message)
            return {
                "assistantResponse": response["assistantResponse"],
                "references": response["references"],
                "confidence": response["confidence"],
                "model": response.get("model", provider_name or "unknown"),
                "sessionId": session_id,
            }
        except ValueError as e:
            return {
                "assistantResponse": (
                    "I cannot answer because no AI provider is configured. "
                    f"Reason: {str(e)}. "
                    "Go to Settings (Command Palette: 'AI Provider: Configure') to set up a provider."
                ),
                "references": [],
                "confidence": "low",
                "error": "PROVIDER_NOT_CONFIGURED",
                "sessionId": session_id,
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "CHAT_FAILED", "message": str(e)})


@router.get("/chat/history")
async def get_chat_history():
    """Return chat history (stub - not yet persisted)."""
    return {"messages": []}


@router.delete("/chat/history")
async def delete_chat_history():
    """Clear chat history (stub)."""
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
# Recommendations, Experiments, Files
# ---------------------------------------------------------------------------

@router.get("/recommendations")
async def get_recommendations():
    """Return current recommendations (stub - returns empty until a report is generated)."""
    return {"recommendations": []}


@router.post("/recommendations/refresh")
async def refresh_recommendations():
    """Regenerate recommendations (stub)."""
    return {"recommendations": []}


@router.get("/report")
async def get_report():
    """Return the latest engineering report (stub - not yet persisted to storage)."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "No report available. Run POST /api/v1/project/analyze first."},
    )


@router.get("/experiments")
async def list_experiments():
    """List experiments (stub)."""
    return {"experiments": []}


@router.get("/logs")
async def get_logs():
    """Return recent log entries (dev only)."""
    return {"logs": []}


@router.get("/metrics")
async def get_metrics():
    """Return performance metrics."""
    return {"uptime_seconds": 0, "requests_total": 0}

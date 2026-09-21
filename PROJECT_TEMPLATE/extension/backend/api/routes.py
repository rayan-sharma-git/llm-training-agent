"""FastAPI route handlers."""
from __future__ import annotations

import difflib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models.schemas import (
    ProjectContext,
    DatasetAnalysisResult,
    DatasetCleaningResult,
    PromptAnalysisResult,
    HyperparameterAnalysisResult,
    ModelAnalysisResult,
    PredictionResult,
    CostEstimate,
    GPUTimeEstimate,
    CalibrationResult,
    HardwareInfo,
    GPUInfo,
    Recommendation,
    EngineeringReport,
    ApiError,
)
from hardware.gpu_detector import detect_gpus, detect_gpus_dict, GPUSpec
from hardware.gpu_time_estimator import (
    GPUTimeEstimator,
    TrainingConfig,
    extract_training_config_from_context,
    run_calibration_benchmark,
)
from scanner.scanner import ProjectScanner
from scanner.context_builder import ContextBuilder
from analyzers.dataset_analyzer import DatasetAnalyzer
from analyzers.prompt_analyzer import PromptAnalyzer
from cleaning.dataset_cleaner import DatasetCleaner
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

def _as_bool(value: Any, default: bool = False) -> bool:
    """Coerce a JSON/string flag into a bool (used for optional request flags)."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("1", "true", "yes", "on", "enabled")


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
async def analyze_project(request: Dict[str, Any]):
    """Analyze an entire fine-tuning project.

    Request body:  {"projectPath": "/path/to/project"}

    Optional flag: {"cleanDatasets": true} additionally runs the chunked
    dataset cleaning pipeline (one LLM request per chunk, all dataset files)
    and returns its summary under the ``cleaning`` key.
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
        dataset_result_obj = None
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
        hp_result_obj = None
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

        # Cost estimation (receives the real dataset & hyperparameter results so
        # the estimates are derived from measured values, not placeholders)
        try:
            cost_result_obj = await cost_estimator.analyze(
                context, dataset_result=dataset_result_obj, hp_result=hp_result_obj,
            )
            results["cost"] = cost_result_obj.model_dump()
        except Exception as e:
            logger.error(f"CostEstimator failed: {e}")
            results["cost"] = {"error": str(e), "confidence": "low"}

        logger.info("All analyzers completed (with possible partial failures)")

        # Step 3b: Optional chunked dataset cleaning (opt-in, one LLM call per chunk)
        if _as_bool(request.get("cleanDatasets"), False) and context.dataset_paths:
            try:
                cleaner = DatasetCleaner()
                cleaning_result = await cleaner.clean_project(context)
                results["dataset_cleaning"] = cleaning_result.model_dump()
                logger.info(
                    f"Dataset cleaning finished: {cleaning_result.total_files} file(s), "
                    f"{cleaning_result.total_chunks} chunk(s), "
                    f"records preserved={cleaning_result.records_preserved}"
                )
            except Exception as e:
                logger.error(f"Dataset cleanup failed: {e}")
                results["dataset_cleaning"] = {"error": str(e)}

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

        # Step 5b: GPU detection & time estimation (integrated into analysis)
        gpu_time_estimate = None
        hardware_result = None
        try:
            from hardware.gpu_detector import detect_gpus
            from hardware.gpu_time_estimator import (
                GPUTimeEstimator,
                extract_training_config_from_context,
            )

            hardware_result = detect_gpus().to_dict()
            training_config = extract_training_config_from_context(context)
            estimator = GPUTimeEstimator()
            estimate_result = estimator.estimate(training_config, mode="quick")
            gpu_time_estimate = estimate_result.to_dict()
        except Exception as e:
            logger.warning(f"GPU time estimation failed during analysis: {e}")

        # Step 6: Report
        try:
            report_gen = ReportGenerator()
            report = report_gen.generate(
                context, ds_result, prompt_result, hp_result, model_result,
                cost_result, prediction_result, recommendations,
                gpu_time_estimate=gpu_time_estimate,
                hardware_detection=hardware_result,
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

        response: Dict[str, Any] = {
            "project": context.model_dump(),
            "report": report.model_dump(),
        }
        if results.get("dataset_cleaning") is not None:
            response["cleaning"] = results["dataset_cleaning"]
        return response

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


@router.post("/dataset/clean", response_model=DatasetCleaningResult)
async def clean_datasets(request: Dict[str, Any]):
    """Clean every dataset file of a project in LLM-sized chunks.

    Request body (all fields optional except a project or dataset reference):

    ```json
    {
      "projectPath": "/path/to/project",
      "datasetPaths": ["data/train.jsonl", "data/val.jsonl"],
      "chunkSize": 25,
      "maxChunkChars": 12000,
      "outputDirectory": ".llm-training-agent/cleaned",
      "maxFiles": 0,
      "useLlm": true
    }
    ```

    * Every dataset file is discovered (a directory entry is expanded
      recursively), then split into sequential chunks of ``chunkSize`` records
      (and at most ``maxChunkChars`` characters).
    * Each chunk is sent to the AI provider in its own request, so an entire
      dataset is never sent in a single call.
    * Cleaned files are written per source file, preserving the relative path
      and format, together with a manifest for verification.  Every record of
      every file is preserved; a chunk that fails validation keeps its original
      records instead of losing data.
    """
    try:
        from pathlib import Path

        project_path = request.get("projectPath")
        dataset_paths = list(request.get("datasetPaths") or [])

        if not project_path and not dataset_paths:
            raise HTTPException(
                status_code=400,
                detail="Either projectPath or datasetPaths is required.",
            )

        if project_path:
            if not Path(project_path).exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"Project path does not exist: {project_path}",
                )
            # Discover dataset files with the same rules the scanner uses.
            if not dataset_paths:
                scanner = ProjectScanner(project_path)
                dataset_paths = scanner.discover_datasets()
                if not dataset_paths:
                    raise HTTPException(
                        status_code=404,
                        detail="No dataset files were found in this project.",
                    )
        else:
            first = Path(str(dataset_paths[0]))
            project_path = str(first.parent if first.is_absolute() else Path.cwd())

        chunk_size = int(request.get("chunkSize") or 0)
        max_chunk_chars = int(request.get("maxChunkChars") or 0)
        max_files = int(request.get("maxFiles") or 0)

        cleaner = DatasetCleaner(
            chunk_size=chunk_size or 25,
            max_chunk_chars=max_chunk_chars or 12000,
        )

        context = ProjectContext(
            project_name=Path(str(project_path)).name or "dataset_cleanup",
            project_path=str(project_path),
            dataset_paths=dataset_paths,
        )

        logger.info(f"Cleaning {len(dataset_paths)} dataset entry(ies) of {project_path}")
        result = await cleaner.clean_project(
            context,
            output_dir=request.get("outputDirectory"),
            max_files=max_files,
            use_llm=_as_bool(request.get("useLlm"), True),
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dataset cleaning failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"errorCode": "CLEANING_FAILED", "message": str(e)},
        )


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
# GPU detection & time estimation
# ---------------------------------------------------------------------------

@router.get("/gpu/detect")
async def detect_gpu_hardware():
    """Detect GPU hardware on the current machine."""
    try:
        hardware = detect_gpus()
        return hardware.to_dict()
    except Exception as e:
        logger.error(f"GPU detection failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "GPU_DETECTION_FAILED", "message": str(e)})


@router.get("/gpu/specs")
async def list_gpu_specs():
    """List known GPU specifications in the performance database."""
    return {"gpus": GPUSpec.get_known_keys()}


@router.post("/gpu/estimate")
async def estimate_gpu_time(request: Dict[str, Any]):
    """Estimate GPU training time.

    Request body:
    {
        "projectPath": "/path/to/project",  # optional - uses existing context
        "mode": "quick" | "calibrated",     # default: quick
        "measuredStepsPerSec": 2.84,        # optional - for calibrated mode
        "config": {                          # optional - override training config
            "modelName": "TinyLlama 1.1B",
            "paramCountBillions": 1.1,
            "datasetSamples": 50000,
            "sequenceLength": 512,
            "batchSize": 4,
            "gradientAccumulation": 8,
            "epochs": 3,
            "maxSteps": null,
            "precision": "4bit",
            "trainingMethod": "qlora",
            "gradientCheckpointing": false,
            "dataloaderWorkers": 0,
            "framework": "huggingface",
            "distributedStrategy": "single"
        }
    }
    """
    try:
        # Build training config
        config_data = request.get("config") or {}
        training_config = TrainingConfig(
            model_name=config_data.get("modelName"),
            param_count_billions=config_data.get("paramCountBillions"),
            dataset_samples=config_data.get("datasetSamples"),
            sequence_length=config_data.get("sequenceLength", 512),
            batch_size=config_data.get("batchSize", 8),
            gradient_accumulation=config_data.get("gradientAccumulation", 1),
            epochs=config_data.get("epochs", 3),
            max_steps=config_data.get("maxSteps"),
            precision=config_data.get("precision", "fp16"),
            training_method=config_data.get("trainingMethod", "full"),
            gradient_checkpointing=config_data.get("gradientCheckpointing", False),
            dataloader_workers=config_data.get("dataloaderWorkers", 0),
            framework=config_data.get("framework", "huggingface"),
            distributed_strategy=config_data.get("distributedStrategy", "single"),
        )

        # If projectPath provided, try to extract config from project
        project_path = request.get("projectPath")
        if project_path and not config_data:
            try:
                scanner = ProjectScanner(project_path)
                scan_result = scanner.scan()
                context_builder = ContextBuilder()
                context = context_builder.build(scan_result)
                training_config = extract_training_config_from_context(context)
            except Exception as e:
                logger.warning(f"Failed to extract config from project: {e}")

        mode = request.get("mode", "quick")
        measured_steps = request.get("measuredStepsPerSec")

        estimator = GPUTimeEstimator()
        result = estimator.estimate(training_config, mode=mode, measured_steps_per_sec=measured_steps)
        return result.to_dict()
    except Exception as e:
        logger.error(f"GPU time estimation failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "GPU_ESTIMATION_FAILED", "message": str(e)})


@router.post("/gpu/calibrate")
async def calibrate_gpu(request: Dict[str, Any]):
    """Run a short calibration benchmark to measure actual GPU throughput.

    Request body:
    {
        "durationSeconds": 30,  # optional - default 30, max 60
        "config": {              # optional - training config for benchmark
            "batchSize": 4,
            "sequenceLength": 512,
            "paramCountBillions": 1.1
        }
    }
    """
    try:
        duration = request.get("durationSeconds", 30)
        config_data = request.get("config") or {}
        training_config = TrainingConfig(
            batch_size=config_data.get("batchSize", 4),
            sequence_length=config_data.get("sequenceLength", 512),
            param_count_billions=config_data.get("paramCountBillions"),
        )
        result = run_calibration_benchmark(training_config, duration_seconds=duration)
        return result
    except Exception as e:
        logger.error(f"Calibration benchmark failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "CALIBRATION_FAILED", "message": str(e)})


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


# ---------------------------------------------------------------------------
# File changes: propose → view → apply/discard → rollback (View Changes)
# ---------------------------------------------------------------------------

from editing.file_editor import PendingChangeStore  # noqa: E402


def _pending_store(project_root: Optional[str]) -> PendingChangeStore:
    root = (project_root or "").strip() or str(Path.cwd())
    return PendingChangeStore(Path(root))


@router.post("/files/propose")
async def propose_file_change(request: Dict[str, Any]):
    """Propose new content for a file without modifying it.

    Returns the change id and a unified diff the UI can render in a diff
    editor before the user decides to apply or discard the change.
    """
    try:
        file_path = (request.get("filePath") or "").strip()
        proposed_content = request.get("proposedContent")
        if not file_path:
            raise HTTPException(status_code=422, detail="filePath must not be empty")
        if proposed_content is None or not isinstance(proposed_content, str):
            raise HTTPException(status_code=422, detail="proposedContent must be a string")

        store = _pending_store(request.get("projectRoot"))
        target = store.project_file(file_path)
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

        original_content = target.read_text(encoding="utf-8")
        diff = "".join(
            difflib.unified_diff(
                original_content.splitlines(keepends=True),
                proposed_content.splitlines(keepends=True),
                fromfile=f"a/{file_path}",
                tofile=f"b/{file_path}",
            )
        )
        record = store.save(
            file_path=file_path,
            original_content=original_content,
            proposed_content=proposed_content,
            diff=diff,
        )
        return record
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Propose file change failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "PROPOSE_FAILED", "message": str(e)})


@router.get("/files/changes")
async def list_file_changes(projectRoot: Optional[str] = None):
    """List pending file-change proposals (metadata only, no contents)."""
    try:
        store = _pending_store(projectRoot)
        return {"changes": store.list()}
    except Exception as e:
        logger.error(f"List file changes failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "LIST_CHANGES_FAILED", "message": str(e)})


@router.get("/files/changes/{change_id}")
async def get_file_change(change_id: str, projectRoot: Optional[str] = None, includeContents: bool = True):
    """Return one change proposal, optionally including original/proposed contents."""
    try:
        store = _pending_store(projectRoot)
        record = store.get(change_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Change not found: {change_id}")
        if not includeContents:
            return {
                k: v for k, v in record.items()
                if k not in ("originalContent", "proposedContent")
            }
        return record
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file change failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "GET_CHANGE_FAILED", "message": str(e)})


@router.post("/files/changes/{change_id}/apply")
async def apply_file_change(change_id: str, request: Dict[str, Any]):
    """Apply an approved change, keeping a backup of the original for rollback."""
    try:
        store = _pending_store(request.get("projectRoot"))
        record = store.get(change_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Change not found: {change_id}")
        if record.get("status") != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Change {change_id} is not pending (status: {record.get('status')})",
            )

        target = store.project_file(record["filePath"])
        if not target.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {record['filePath']}")

        backup_dir = store.project_root / ".llm_training_agent_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{target.name}.{change_id}.bak"
        backup_path.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")

        target.write_text(record["proposedContent"], encoding="utf-8")
        store.set_status(change_id, "applied", backup_path=str(backup_path))
        return {
            "changeId": change_id,
            "filePath": record["filePath"],
            "status": "applied",
            "backupPath": str(backup_path),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Apply file change failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "APPLY_FAILED", "message": str(e)})


@router.post("/files/changes/{change_id}/discard")
async def discard_file_change(change_id: str, request: Dict[str, Any]):
    """Reject a pending change without touching the file."""
    try:
        store = _pending_store(request.get("projectRoot"))
        record = store.get(change_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Change not found: {change_id}")
        if record.get("status") == "applied":
            raise HTTPException(
                status_code=409,
                detail="Change already applied. Use rollback instead of discard.",
            )
        store.set_status(change_id, "rejected")
        store.remove(change_id)
        return {"changeId": change_id, "status": "rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Discard file change failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "DISCARD_FAILED", "message": str(e)})


@router.post("/files/changes/{change_id}/rollback")
async def rollback_file_change(change_id: str, request: Dict[str, Any]):
    """Restore a file to its pre-apply state from the stored backup."""
    try:
        store = _pending_store(request.get("projectRoot"))
        record = store.get(change_id)
        if not record:
            raise HTTPException(status_code=404, detail=f"Change not found: {change_id}")
        backup_str = record.get("backupPath")
        if record.get("status") != "applied" or not backup_str:
            raise HTTPException(status_code=409, detail="Change has not been applied; nothing to roll back")

        backup_path = Path(backup_str)
        if not backup_path.exists():
            raise HTTPException(status_code=404, detail=f"Backup not found: {backup_path}")

        target = store.project_file(record["filePath"])
        target.write_text(backup_path.read_text(encoding="utf-8"), encoding="utf-8")
        store.set_status(change_id, "rolled_back")
        store.remove(change_id)
        return {"changeId": change_id, "filePath": record["filePath"], "status": "rolled_back"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rollback file change failed: {e}")
        raise HTTPException(status_code=500, detail={"errorCode": "ROLLBACK_FAILED", "message": str(e)})

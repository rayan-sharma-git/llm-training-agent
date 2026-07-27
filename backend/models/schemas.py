"""Pydantic schemas matching JSON schemas."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Confidence(str, Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Difficulty(str, Enum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class PromptComplexity(str, Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class Capability(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PredictionQuality(str, Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class SpeedScore(str, Enum):
    SLOW = "slow"
    MEDIUM = "medium"
    FAST = "fast"


class Risk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class ProjectContext(BaseModel):
    schema_version: str = "1.0"
    project_name: str
    project_path: str
    detected_framework: Optional[str] = None
    framework_version: Optional[str] = None
    base_model: Optional[str] = None
    tokenizer: Optional[str] = None
    dataset_paths: List[str] = []
    prompt_templates: List[str] = []
    configuration_files: List[str] = []
    training_scripts: List[str] = []
    evaluation_scripts: List[str] = []
    inference_scripts: List[str] = []
    hardware_information: Dict[str, Any] = {}
    project_statistics: Dict[str, Any] = {}
    project_health_score: Optional[float] = None
    training_readiness_score: Optional[float] = None
    analysis_timestamp: Optional[datetime] = None


class DatasetAnalysisResult(BaseModel):
    schema_version: str = "1.0"
    dataset_name: str
    sample_count: int
    token_count: int
    average_prompt_length: float
    average_response_length: float
    duplicate_percentage: float
    near_duplicate_percentage: float
    missing_field_percentage: float
    formatting_consistency_score: float
    language_consistency_score: float
    instruction_consistency_score: float
    response_consistency_score: float
    quality_score: float
    findings: List[str] = []
    warnings: List[str] = []
    recommendations: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class PromptAnalysisResult(BaseModel):
    schema_version: str = "1.0"
    template_name: str
    prompt_complexity: PromptComplexity = PromptComplexity.MODERATE
    ambiguity_score: float
    clarity_score: float
    formatting_score: float
    instruction_quality_score: float
    consistency_score: float
    detected_issues: List[str] = []
    recommendations: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class HyperparameterAnalysisResult(BaseModel):
    schema_version: str = "1.0"
    learning_rate: Optional[float] = None
    batch_size: Optional[int] = None
    epochs: Optional[int] = None
    optimizer: Optional[str] = None
    scheduler: Optional[str] = None
    gradient_accumulation: Optional[int] = None
    weight_decay: Optional[float] = None
    warmup_ratio: Optional[float] = None
    sequence_length: Optional[int] = None
    lora_rank: Optional[int] = None
    lora_alpha: Optional[int] = None
    lora_dropout: Optional[float] = None
    overfitting_risk: Risk = Risk.LOW
    underfitting_risk: Risk = Risk.LOW
    efficiency_score: float
    recommendations: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class ModelAnalysisResult(BaseModel):
    schema_version: str = "1.0"
    selected_model: str
    parameter_count: str
    context_length: int
    estimated_vram: str
    reasoning_capability: Capability = Capability.MEDIUM
    coding_capability: Capability = Capability.MEDIUM
    multilingual_capability: Capability = Capability.MEDIUM
    instruction_following_capability: Capability = Capability.MEDIUM
    speed_score: SpeedScore = SpeedScore.MEDIUM
    memory_efficiency: Capability = Capability.MEDIUM
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommended_alternatives: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class PredictionResult(BaseModel):
    schema_version: str = "1.0"
    instruction_following_prediction: PredictionQuality = PredictionQuality.FAIR
    hallucination_risk: Risk = Risk.MEDIUM
    reasoning_prediction: PredictionQuality = PredictionQuality.FAIR
    response_consistency_prediction: PredictionQuality = PredictionQuality.FAIR
    creativity_prediction: Capability = Capability.MEDIUM
    formatting_prediction: PredictionQuality = PredictionQuality.FAIR
    likely_failure_modes: List[str] = []
    expected_strengths: List[str] = []
    expected_weaknesses: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class CostEstimate(BaseModel):
    schema_version: str = "1.0"
    estimated_training_time: str
    estimated_gpu_hours: float
    estimated_vram_usage: str
    estimated_checkpoint_size: str
    estimated_storage_requirement: str
    compatible_hardware: List[str] = []
    assumptions: List[str] = []
    confidence: Confidence = Confidence.MEDIUM


class Recommendation(BaseModel):
    schema_version: str = "1.0"
    recommendation_id: str = Field(default_factory=lambda: "rec-00000000-0000-0000-0000-000000000000")
    category: str
    title: str
    description: str
    reasoning: str
    evidence: str
    severity: Severity = Severity.MEDIUM
    confidence: Confidence = Confidence.MEDIUM
    estimated_benefit: str
    implementation_difficulty: Difficulty = Difficulty.MODERATE
    estimated_engineering_time: str
    affected_files: List[str] = []
    suggested_actions: List[str] = []
    references: List[str] = []


class EngineeringReport(BaseModel):
    schema_version: str = "1.0"
    executive_summary: str
    project_health_score: float
    training_readiness_score: float
    dataset_summary: Dict[str, Any] = {}
    prompt_summary: Dict[str, Any] = {}
    hyperparameter_summary: Dict[str, Any] = {}
    model_summary: Dict[str, Any] = {}
    prediction_summary: Dict[str, Any] = {}
    cost_summary: Dict[str, Any] = {}
    prioritized_recommendations: List[Recommendation] = []
    action_plan: List[str] = []


class ChatMessage(BaseModel):
    schema_version: str = "1.0"
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Experiment(BaseModel):
    schema_version: str = "1.0"
    base_model: str
    dataset_version: str
    tokenizer: Optional[str] = None
    hyperparameters: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    notes: str = ""
    tags: List[str] = []
    artifacts: List[str] = []


class FileModification(BaseModel):
    schema_version: str = "1.0"
    file_path: str
    modification_type: str
    original_content: Optional[str] = None
    proposed_content: Optional[str] = None
    diff: Optional[str] = None
    approval_status: str = "pending"
    applied_timestamp: Optional[datetime] = None
    rollback_available: bool = False


class ApiError(BaseModel):
    schema_version: str = "1.0"
    error_code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
"""Pydantic schemas for all data models."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectContext(BaseModel):
    """Structured project representation."""
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
    """Dataset analysis results."""
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
    confidence: str = "medium"


class PromptAnalysisResult(BaseModel):
    """Prompt analysis results."""
    template_name: str
    prompt_complexity: str = "moderate"
    ambiguity_score: float
    clarity_score: float
    formatting_score: float
    instruction_quality_score: float
    consistency_score: float
    detected_issues: List[str] = []
    recommendations: List[str] = []
    confidence: str = "medium"


class HyperparameterAnalysisResult(BaseModel):
    """Hyperparameter analysis results."""
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
    overfitting_risk: str = "medium"
    underfitting_risk: str = "medium"
    efficiency_score: float
    recommendations: List[str] = []
    confidence: str = "medium"


class ModelAnalysisResult(BaseModel):
    """Model analysis results."""
    selected_model: str
    parameter_count: str
    context_length: int
    estimated_vram: str
    reasoning_capability: str = "medium"
    coding_capability: str = "medium"
    multilingual_capability: str = "medium"
    instruction_following_capability: str = "medium"
    speed_score: str = "medium"
    memory_efficiency: str = "medium"
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommended_alternatives: List[str] = []
    confidence: str = "medium"


class PredictionResult(BaseModel):
    """Training outcome predictions."""
    instruction_following_prediction: str = "fair"
    hallucination_risk: str = "medium"
    reasoning_prediction: str = "fair"
    response_consistency_prediction: str = "fair"
    creativity_prediction: str = "medium"
    formatting_prediction: str = "fair"
    likely_failure_modes: List[str] = []
    expected_strengths: List[str] = []
    expected_weaknesses: List[str] = []
    confidence: str = "medium"


class CostEstimate(BaseModel):
    """Training cost estimates."""
    estimated_training_time: str
    estimated_gpu_hours: float
    estimated_vram_usage: str
    estimated_checkpoint_size: str
    estimated_storage_requirement: str
    compatible_hardware: List[str] = []
    assumptions: List[str] = []
    confidence: str = "medium"


class Recommendation(BaseModel):
    """Single recommendation."""
    recommendation_id: str
    category: str
    title: str
    description: str
    reasoning: str
    evidence: str
    severity: str = "medium"
    confidence: str = "medium"
    estimated_benefit: str = ""
    implementation_difficulty: str = "moderate"
    estimated_engineering_time: str = ""
    affected_files: List[str] = []
    suggested_actions: List[str] = []
    references: List[str] = []


class EngineeringReport(BaseModel):
    """Complete engineering report."""
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
    """A single message in a chat conversation."""
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiError(BaseModel):
    """API error response."""
    error_code: str
    message: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
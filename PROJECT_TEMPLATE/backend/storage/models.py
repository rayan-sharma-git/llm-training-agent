"""SQLAlchemy ORM models."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Index,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from storage.database import Base


class Project(Base):
    """Project metadata table."""

    __tablename__ = "projects"

    project_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_name = Column(String(255), nullable=False)
    project_path = Column(String(1024), nullable=False, unique=True)
    framework = Column(String(100))
    framework_version = Column(String(50))
    base_model = Column(String(255))
    tokenizer = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    analyses = relationship("Analysis", back_populates="project", cascade="all, delete-orphan")
    experiments = relationship("Experiment", back_populates="project", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="project", cascade="all, delete-orphan")
    file_modifications = relationship("FileModification", back_populates="project", cascade="all, delete-orphan")


class Analysis(Base):
    """Analysis session table."""

    __tablename__ = "analyses"

    analysis_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration = Column(Integer)
    health_score = Column(Float)
    readiness_score = Column(Float)
    status = Column(String(50), default="running")

    project = relationship("Project", back_populates="analyses")
    dataset_report = relationship("DatasetReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    prompt_report = relationship("PromptReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    hyperparameter_report = relationship("HyperparameterReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    model_report = relationship("ModelReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    prediction = relationship("Prediction", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    cost_estimate = relationship("CostEstimateRecord", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    recommendations = relationship("RecommendationRecord", back_populates="analysis", cascade="all, delete-orphan")


class DatasetReport(Base):
    """Dataset analysis report table."""

    __tablename__ = "dataset_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    dataset_name = Column(String(255), nullable=False)
    quality_score = Column(Float)
    duplicate_percentage = Column(Float)
    token_count = Column(Integer)
    findings = Column(JSON)
    recommendations = Column(JSON)

    analysis = relationship("Analysis", back_populates="dataset_report")


class PromptReport(Base):
    """Prompt analysis report table."""

    __tablename__ = "prompt_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    template_name = Column(String(255), nullable=False)
    clarity_score = Column(Float)
    ambiguity_score = Column(Float)
    consistency_score = Column(Float)
    findings = Column(JSON)
    recommendations = Column(JSON)

    analysis = relationship("Analysis", back_populates="prompt_report")


class HyperparameterReport(Base):
    """Hyperparameter analysis report table."""

    __tablename__ = "hyperparameter_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    learning_rate = Column(Float)
    batch_size = Column(Integer)
    epochs = Column(Integer)
    optimizer = Column(String(100))
    scheduler = Column(String(100))
    lora_rank = Column(Integer)
    lora_alpha = Column(Integer)
    findings = Column(JSON)
    recommendations = Column(JSON)

    analysis = relationship("Analysis", back_populates="hyperparameter_report")


class ModelReport(Base):
    """Model analysis report table."""

    __tablename__ = "model_reports"

    report_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    model_name = Column(String(255), nullable=False)
    reasoning_score = Column(Float)
    coding_score = Column(Float)
    speed_score = Column(Float)
    vram_estimate = Column(String(100))
    strengths = Column(JSON)
    weaknesses = Column(JSON)

    analysis = relationship("Analysis", back_populates="model_report")


class Prediction(Base):
    """Training outcome prediction table."""

    __tablename__ = "predictions"

    prediction_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    confidence = Column(Float)
    hallucination_risk = Column(Float)
    reasoning_prediction = Column(Float)
    instruction_following_prediction = Column(Float)
    response_consistency = Column(Float)
    predicted_failure_modes = Column(JSON)

    analysis = relationship("Analysis", back_populates="prediction")


class CostEstimateRecord(Base):
    """Cost estimate table."""

    __tablename__ = "cost_estimates"

    estimate_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    training_time = Column(String(100))
    gpu_hours = Column(Float)
    vram = Column(String(100))
    storage = Column(String(100))
    checkpoint_size = Column(String(100))

    analysis = relationship("Analysis", back_populates="cost_estimate")


class RecommendationRecord(Base):
    """Recommendation table."""

    __tablename__ = "recommendations"

    recommendation_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.analysis_id"), nullable=False)
    severity = Column(String(50))
    confidence = Column(Float)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    evidence = Column(Text)
    status = Column(String(50), default="pending")

    analysis = relationship("Analysis", back_populates="recommendations")


class Experiment(Base):
    """Experiment tracking table."""

    __tablename__ = "experiments"

    experiment_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    dataset_version = Column(String(255), nullable=False)
    model = Column(String(255), nullable=False)
    tokenizer = Column(String(255))
    hyperparameters = Column(JSON)
    metrics = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(JSON, default=list)
    artifacts = Column(JSON, default=list)

    project = relationship("Project", back_populates="experiments")


class ChatSession(Base):
    """Chat session table."""

    __tablename__ = "chat_sessions"

    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="chat_sessions")
    messages = relationship("ChatMessageRecord", back_populates="session", cascade="all, delete-orphan")


class ChatMessageRecord(Base):
    """Chat message table."""

    __tablename__ = "chat_messages"

    message_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("chat_sessions.session_id"), nullable=False)
    role = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


class FileModification(Base):
    """File modification tracking table."""

    __tablename__ = "file_modifications"

    modification_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.project_id"), nullable=False)
    file_path = Column(String(1024), nullable=False)
    change_summary = Column(Text)
    approval_status = Column(String(50), default="pending")
    rollback_available = Column(Boolean, default=False)
    applied_at = Column(DateTime(timezone=True))

    project = relationship("Project", back_populates="file_modifications")


class Setting(Base):
    """Key-value settings table."""

    __tablename__ = "settings"

    key = Column(String(255), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
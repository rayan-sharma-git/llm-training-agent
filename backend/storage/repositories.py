"""Repository interfaces and implementations."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from storage.models import (
    Analysis,
    ChatMessageRecord,
    ChatSession,
    DatasetReport,
    Experiment,
    FileModification,
    ModelReport,
    Prediction,
    PromptReport,
    Project,
    RecommendationRecord,
)


class ProjectRepository:
    """Project data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, project: Project) -> Project:
        self.session.add(project)
        await self.session.flush()
        return project

    async def get_by_path(self, path: str) -> Optional[Project]:
        result = await self.session.execute(select(Project).where(Project.project_path == path))
        return result.scalar_one_or_none()

    async def get_by_id(self, project_id: str) -> Optional[Project]:
        result = await self.session.execute(select(Project).where(Project.project_id == project_id))
        return result.scalar_one_or_none()

    async def list_all(self) -> List[Project]:
        result = await self.session.execute(select(Project).order_by(Project.created_at.desc()))
        return list(result.scalars().all())

    async def delete(self, project_id: str) -> bool:
        project = await self.get_by_id(project_id)
        if project:
            await self.session.delete(project)
            return True
        return False


class AnalysisRepository:
    """Analysis data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, analysis: Analysis) -> Analysis:
        self.session.add(analysis)
        await self.session.flush()
        return analysis

    async def get_by_id(self, analysis_id: str) -> Optional[Analysis]:
        result = await self.session.execute(select(Analysis).where(Analysis.analysis_id == analysis_id))
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: str) -> List[Analysis]:
        result = await self.session.execute(
            select(Analysis).where(Analysis.project_id == project_id).order_by(Analysis.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_latest_for_project(self, project_id: str) -> Optional[Analysis]:
        result = await self.session.execute(
            select(Analysis).where(Analysis.project_id == project_id).order_by(Analysis.started_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def update_status(self, analysis_id: str, status: str, completed_at: Optional[datetime] = None) -> Optional[Analysis]:
        analysis = await self.get_by_id(analysis_id)
        if analysis:
            analysis.status = status
            if completed_at:
                analysis.completed_at = completed_at
            await self.session.flush()
        return analysis


class DatasetRepository:
    """Dataset report data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report: DatasetReport) -> DatasetReport:
        self.session.add(report)
        await self.session.flush()
        return report

    async def get_by_analysis(self, analysis_id: str) -> Optional[DatasetReport]:
        result = await self.session.execute(
            select(DatasetReport).where(DatasetReport.analysis_id == analysis_id)
        )
        return result.scalar_one_or_none()


class RecommendationRepository:
    """Recommendation data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, rec: RecommendationRecord) -> RecommendationRecord:
        self.session.add(rec)
        await self.session.flush()
        return rec

    async def list_by_analysis(self, analysis_id: str) -> List[RecommendationRecord]:
        result = await self.session.execute(
            select(RecommendationRecord)
            .where(RecommendationRecord.analysis_id == analysis_id)
            .order_by(RecommendationRecord.severity)
        )
        return list(result.scalars().all())

    async def update_status(self, recommendation_id: str, status: str) -> Optional[RecommendationRecord]:
        rec = await self.session.get(RecommendationRecord, recommendation_id)
        if rec:
            rec.status = status
            await self.session.flush()
        return rec


class ExperimentRepository:
    """Experiment data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, experiment: Experiment) -> Experiment:
        self.session.add(experiment)
        await self.session.flush()
        return experiment

    async def get_by_id(self, experiment_id: str) -> Optional[Experiment]:
        return await self.session.get(Experiment, experiment_id)

    async def list_by_project(self, project_id: str) -> List[Experiment]:
        result = await self.session.execute(
            select(Experiment).where(Experiment.project_id == project_id).order_by(Experiment.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, experiment_id: str) -> bool:
        experiment = await self.get_by_id(experiment_id)
        if experiment:
            await self.session.delete(experiment)
            return True
        return False


class ChatRepository:
    """Chat data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_session(self, session: ChatSession) -> ChatSession:
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_session(self, session_id: str) -> Optional[ChatSession]:
        return await self.session.get(ChatSession, session_id)

    async def add_message(self, message: ChatMessageRecord) -> ChatMessageRecord:
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_messages(self, session_id: str, limit: int = 50) -> List[ChatMessageRecord]:
        result = await self.session.execute(
            select(ChatMessageRecord)
            .where(ChatMessageRecord.session_id == session_id)
            .order_by(ChatMessageRecord.timestamp.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))

    async def delete_session(self, session_id: str) -> bool:
        session = await self.get_session(session_id)
        if session:
            await self.session.delete(session)
            return True
        return False


class SettingsRepository:
    """Settings data access."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, key: str) -> Optional[Any]:
        setting = await self.session.get(Setting, key)
        return setting.value if setting else None

    async def set(self, key: str, value: Any) -> Setting:
        setting = await self.session.get(Setting, key)
        if setting:
            setting.value = value
        else:
            setting = Setting(key=key, value=value)
            self.session.add(setting)
        await self.session.flush()
        return setting

    async def list_all(self) -> Dict[str, Any]:
        result = await self.session.execute(select(Setting))
        settings = result.scalars().all()
        return {s.key: s.value for s in settings}
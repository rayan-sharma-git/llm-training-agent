"""Pytest configuration and fixtures."""
from __future__ import annotations

import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from storage.database import Base, get_session_factory
from models.schemas import ProjectContext
from api.routes import router
from core.config import get_settings


def pytest_configure(config):
    config.AsyncClient = AsyncClient
    config.ASGITransport = ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = get_session_factory(engine)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def client(db_session):
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_project_context():
    return ProjectContext(
        project_name="test_project",
        project_path="/tmp/test_project",
        detected_framework="huggingface",
        dataset_paths=["data/train.json"],
        prompt_templates=["prompts/default.txt"],
    )
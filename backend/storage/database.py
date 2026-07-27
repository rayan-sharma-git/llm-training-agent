"""SQLAlchemy async database setup."""
from __future__ import annotations

from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import get_settings


class Base(DeclarativeBase):
    """Base ORM class."""

    pass


def get_engine():
    """Create async SQLAlchemy engine."""
    settings = get_settings()
    db_path = Path(settings.database_url.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(
        settings.database_url.replace("sqlite://", "sqlite+aiosqlite://"),
        echo=settings.database_echo,
    )
    return engine


def get_session_factory(engine):
    """Create async session factory."""
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator:
    """FastAPI dependency for database sessions."""
    engine = get_engine()
    factory = get_session_factory(engine)
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
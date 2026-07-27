"""Database configuration and session management."""
from __future__ import annotations

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from core.config import get_settings


class Base(DeclarativeBase):
    """Base class for ORM models."""
    pass


class Database:
    """Database connection manager."""
    
    def __init__(self, database_url: str):
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def create_tables(self) -> None:
        """Create all tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def dispose(self) -> None:
        """Dispose engine."""
        await self.engine.dispose()


# Global database instance
_db: Database | None = None


def get_database() -> Database:
    """Get database instance."""
    global _db
    if _db is None:
        _db = Database(get_settings().database_url)
    return _db


def get_session_factory() -> async_sessionmaker:
    """Get session factory."""
    return get_database().session_factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Get database session for FastAPI dependency injection."""
    async with get_session_factory()() as session:
        yield session
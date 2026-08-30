"""PostgreSQL database engine and session management."""

from collections.abc import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Sync Engine (for Alembic migrations and synchronous utilities)
sync_db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")
sync_engine = create_engine(
    sync_db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine (for FastAPI async request handlers)
async_db_url = settings.DATABASE_URL
if async_db_url.startswith("postgresql://") or async_db_url.startswith("postgresql+psycopg://"):
    async_db_url = async_db_url.replace("postgresql+psycopg://", "postgresql+asyncpg://").replace("postgresql://", "postgresql+asyncpg://")

async_engine = create_async_engine(
    async_db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_sync_db() -> Generator[Session, None, None]:
    """Yield a synchronous database session."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an asynchronous database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


get_db = get_async_db


async def check_db_health() -> bool:
    """Check database connectivity with fast timeout."""
    import asyncio
    try:
        async def _probe():
            async with AsyncSessionLocal() as session:
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
            return True
        return await asyncio.wait_for(_probe(), timeout=0.5)
    except Exception:
        return False

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

import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

settings = get_settings()


def _sanitize_async_db_url(url: str) -> str:
    """Sanitize database URL specifically for asyncpg compatibility."""
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql+psycopg://"):
        url = url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)

    parsed = urlparse(url)
    if not parsed.query:
        return url

    query_params = parse_qs(parsed.query)
    clean_params: dict[str, str] = {}
    for k, v in query_params.items():
        if k.lower() == "sslmode":
            # asyncpg uses 'ssl' instead of 'sslmode'
            val = v[0]
            clean_params["ssl"] = "require" if val in ("require", "verify-ca", "verify-full", "prefer") else val
        elif k.lower() in ("channel_binding", "target_session_attrs"):
            # libpq / psycopg3 specific parameters ignored by asyncpg
            continue
        else:
            clean_params[k] = v[0]

    new_query = urlencode(clean_params)
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))


def _sanitize_sync_db_url(url: str) -> str:
    """Sanitize database URL for synchronous psycopg/alembic compatibility."""
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


# Sync Engine (for Alembic migrations and synchronous utilities)
sync_db_url = _sanitize_sync_db_url(settings.DATABASE_URL)
sync_engine = create_engine(
    sync_db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Async Engine (for FastAPI async request handlers)
async_db_url = _sanitize_async_db_url(settings.DATABASE_URL)

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

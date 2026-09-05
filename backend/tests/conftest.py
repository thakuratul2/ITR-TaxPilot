"""Pytest test configuration and shared fixtures."""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

import app.models  # noqa: F401
from app.core.config import Settings
from app.db.base import Base
from app.db.session import async_engine
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    """Provide isolated test settings."""
    return Settings(
        APP_NAME="ITR-TaxPilot-Test",
        APP_ENV="test",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        SECRET_KEY="test-secret-key-for-testing",
        ENABLE_PII_MASKING=True,
    )


@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_test_db():
    """Ensure all database tables are created before test sessions if DB is reachable."""
    import asyncio
    try:
        async def _init():
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

        await asyncio.wait_for(_init(), timeout=1.5)
        yield
    except Exception:
        yield


from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.session import get_db


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create a FastAPI TestClient instance with in-memory SQLite DB override."""
    test_db_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    session_factory = async_sessionmaker(test_db_engine, class_=AsyncSession, expire_on_commit=False)

    app = create_app(settings=test_settings)

    async def _test_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _test_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)

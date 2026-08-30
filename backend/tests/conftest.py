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
    """Ensure all database tables are created before test sessions."""
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    except Exception:
        yield


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create a FastAPI TestClient instance."""
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        yield test_client

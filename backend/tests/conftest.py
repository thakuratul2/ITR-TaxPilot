import os
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.config import Settings, get_settings

get_settings.cache_clear()
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture(scope="session")
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


# In-memory test engine with static pool so tables persist across sessions
_test_db_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
_test_session_factory = async_sessionmaker(_test_db_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_test_db():
    """Create all tables in in-memory test database."""
    async with _test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create a FastAPI TestClient instance with in-memory SQLite DB override."""
    app = create_app(settings=test_settings)

    async def _test_get_db():
        async with _test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _test_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)

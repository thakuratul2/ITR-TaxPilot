"""Pytest test configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
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


@pytest.fixture
def client(test_settings: Settings) -> TestClient:
    """Create a FastAPI TestClient instance."""
    app = create_app(settings=test_settings)
    with TestClient(app) as test_client:
        yield test_client

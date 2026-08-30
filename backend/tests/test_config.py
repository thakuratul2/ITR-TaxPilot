"""Tests for application settings and configuration."""

from app.core.config import Settings


def test_settings_defaults():
    """Test default values of Settings."""
    settings = Settings()
    assert settings.APP_NAME == "ITR-TaxPilot"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.MAX_UPLOAD_SIZE_MB == 10
    assert "http://localhost:8000" in settings.cors_origins
    assert "application/pdf" in settings.allowed_mimes


def test_settings_override():
    """Test setting overrides."""
    settings = Settings(
        APP_NAME="Custom-TaxPilot",
        ALLOWED_ORIGINS="https://example.com,https://app.example.com",
    )
    assert settings.APP_NAME == "Custom-TaxPilot"
    assert len(settings.cors_origins) == 2
    assert "https://example.com" in settings.cors_origins

"""Test suite validating Milestone 17: Production Deployment artifacts, Dockerfiles, and compose configurations."""

from pathlib import Path


def test_production_dockerfile_structure():
    """Verify backend/Dockerfile.prod multi-stage build and security configuration."""
    project_root = Path(__file__).resolve().parent.parent.parent
    dockerfile_path = project_root / "backend" / "Dockerfile.prod"

    assert dockerfile_path.exists()
    content = dockerfile_path.read_text(encoding="utf-8")

    assert "FROM python:3.12-slim AS builder" in content
    assert "FROM python:3.12-slim AS runner" in content
    assert "useradd" in content or "appuser" in content  # Unprivileged user
    assert "HEALTHCHECK" in content
    assert "ENTRYPOINT" in content


def test_production_docker_compose():
    """Verify docker-compose.prod.yml includes Nginx, PostgreSQL, Redis, and Backend services."""
    project_root = Path(__file__).resolve().parent.parent.parent
    compose_path = project_root / "docker-compose.prod.yml"

    assert compose_path.exists()
    content = compose_path.read_text(encoding="utf-8")

    assert "nginx:" in content
    assert "backend:" in content
    assert "postgres:" in content
    assert "redis:" in content
    assert "healthcheck:" in content
    assert "resources:" in content
    assert "limits:" in content


def test_production_nginx_configuration():
    """Verify Nginx configuration and security reverse proxy rules."""
    project_root = Path(__file__).resolve().parent.parent.parent
    nginx_conf = project_root / "nginx" / "nginx.conf"
    vhost_conf = project_root / "nginx" / "conf.d" / "taxpilot.conf"

    assert nginx_conf.exists()
    assert vhost_conf.exists()

    vhost_content = vhost_conf.read_text(encoding="utf-8")
    assert "client_max_body_size" in vhost_content
    assert "X-Frame-Options" in vhost_content
    assert "proxy_pass http://backend_cluster" in vhost_content


def test_production_deployment_docs():
    """Verify docs/deployment.md contains complete deployment guidance."""
    project_root = Path(__file__).resolve().parent.parent.parent
    doc_path = project_root / "docs" / "deployment.md"

    assert doc_path.exists()
    content = doc_path.read_text(encoding="utf-8")

    assert "Infrastructure Requirements" in content
    assert "Environment Configuration" in content
    assert "Deployment Steps" in content
    assert "Backup & Restore" in content

"""Unit tests for backend server health check and root endpoints."""

from fastapi.testclient import TestClient

from src.app.core.config import settings
from src.app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify root endpoint returns basic application overview."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["status"] == "online"
    assert data["docs"] == "/docs"
    assert data["api_v1"] == settings.API_V1_STR


def test_root_healthz_alias():
    """Verify root /healthz endpoint returns 200 ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION


def test_api_v1_health_endpoint():
    """Verify detailed /api/v1/health endpoint returns health status and metadata."""
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT
    assert "timestamp" in data


def test_api_v1_livez_probe():
    """Verify container liveness probe endpoint /api/v1/livez."""
    response = client.get(f"{settings.API_V1_STR}/livez")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "timestamp" in data


def test_api_v1_readyz_probe():
    """Verify container readiness probe endpoint /api/v1/readyz."""
    response = client.get(f"{settings.API_V1_STR}/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data
    assert data["checks"]["server"] == "ok"
    assert data["checks"]["api"] == "ready"
    assert "timestamp" in data


def test_lifespan_startup_and_shutdown():
    """Verify application lifespan manager executes cleanly."""
    with TestClient(app) as test_client:
        response = test_client.get("/healthz")
        assert response.status_code == 200


def test_openapi_docs_accessible():
    """Verify OpenAPI documentation and JSON schemas are generated."""
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    openapi_response = client.get("/openapi.json")
    assert openapi_response.status_code == 200
    openapi_data = openapi_response.json()
    assert openapi_data["info"]["title"] == settings.PROJECT_NAME
    assert openapi_data["info"]["version"] == settings.VERSION

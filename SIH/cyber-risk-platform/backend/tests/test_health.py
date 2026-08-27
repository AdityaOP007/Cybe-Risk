"""
Tests for root and health endpoints.

Verifies the foundational API endpoints are responding correctly.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for GET /"""

    def test_root_returns_200(self) -> None:
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_app_name(self) -> None:
        response = client.get("/")
        data = response.json()
        assert data["name"] == "Cyber Risk Platform"
        assert data["status"] == "running"


class TestHealthEndpoint:
    """Tests for GET /api/v1/health"""

    def test_health_returns_200(self) -> None:
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self) -> None:
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] == "healthy"

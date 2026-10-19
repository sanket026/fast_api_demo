from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.db.session import get_db
from app.main import app


def test_health_check(client: TestClient) -> None:
    """Test the basic /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "environment" in data


def test_readiness_check_success(client: TestClient) -> None:
    """Test the /health/ready endpoint when database is connected."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_readiness_check_failure(client: TestClient) -> None:
    """Test the /health/ready endpoint when database execution fails."""
    mock_session = MagicMock()
    mock_session.execute.side_effect = Exception("Simulated DB connection failure")

    def mock_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = mock_get_db
    try:
        response = client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["error"] == "DatabaseConnectionError"
        assert "Database connection failed" in data["detail"]
    finally:
        app.dependency_overrides.clear()


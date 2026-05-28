from fastapi.testclient import TestClient
from src.main import app


def test_read_stats():
    with TestClient(app) as client:
        response = client.get("/stats")
        assert response.status_code == 200
        assert "total_visits" in response.json()
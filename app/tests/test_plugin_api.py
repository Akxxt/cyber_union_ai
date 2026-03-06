from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_plugins():
    response = client.get("/api/v1/plugins", headers={"X-API-Key": "default_secret"})
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert isinstance(data["data"], list)


def test_plugin_enable_disable():
    response = client.post("/api/v1/plugins/file_operation/enable", headers={"X-API-Key": "default_secret"})
    assert response.status_code in (200, 404)
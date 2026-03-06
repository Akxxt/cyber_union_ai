import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "status" in data["data"]


@pytest.mark.asyncio
async def test_create_task_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/tasks", json={"input": "test"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_task_authorized():
    headers = {"X-API-Key": "default_secret"}
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/tasks", json={"input": "test"}, headers=headers)
    assert response.status_code == 200
    assert "task_id" in response.json()["data"]
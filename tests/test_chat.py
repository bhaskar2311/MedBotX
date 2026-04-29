"""
MedBotX - Chat API Tests
Developed by Bhaskar Shivaji Kumbhar
"""
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["developer"] == "Bhaskar Shivaji Kumbhar"


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "MedBotX" in data["app"]


@pytest.mark.asyncio
async def test_new_session():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/v1/chat/session/new", json={})
    assert resp.status_code == 200
    assert "session_id" in resp.json()


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        reg = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "email": "test@example.com", "password": "Test1234!"},
        )
        assert reg.status_code in (201, 409)

        login = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "Test1234!"},
        )
        if reg.status_code == 201:
            assert login.status_code == 200
            assert "access_token" in login.json()

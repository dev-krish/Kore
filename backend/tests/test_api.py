import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

async def get_auth_headers(ac: AsyncClient) -> dict:
    res = await ac.get("/api/auth/demo-session")
    assert res.status_code == 200
    token = res.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_root_and_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/")
        assert res.status_code == 200
        assert res.json()["product"] == "KORE"

        res_health = await ac.get("/health")
        assert res_health.status_code == 200
        assert res_health.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_profile_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)
        res = await ac.get("/api/profiles/me", headers=headers)
        assert res.status_code == 200
        profile = res.json()
        assert "fullName" in profile
        assert "skills" in profile

        # Update profile
        res_put = await ac.put("/api/profiles/me", json={"fullName": "Test Student Updated"}, headers=headers)
        assert res_put.status_code == 200
        assert res_put.json()["fullName"] == "Test Student Updated"

@pytest.mark.asyncio
async def test_campaign_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)
        camp_payload = {
            "name": "API Test Campaign",
            "objective": "Discover 2 AI startups for software internship",
            "targetIndustry": "AI Startups",
            "targetLocation": "Bengaluru",
            "targetRoles": ["Founders"],
            "targetProspectCount": 2,
            "preferredTechnologies": ["Python", "FastAPI"]
        }
        res = await ac.post("/api/campaigns", json=camp_payload, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "_id" in data
        assert data["name"] == "API Test Campaign"

        # List campaigns
        res_list = await ac.get("/api/campaigns", headers=headers)
        assert res_list.status_code == 200
        assert len(res_list.json()) > 0

@pytest.mark.asyncio
async def test_integrations_status_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)
        res = await ac.get("/api/integrations/status", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "ollama" in data
        assert "search" in data
        assert "gmail" in data

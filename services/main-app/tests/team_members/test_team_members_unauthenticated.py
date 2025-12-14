import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_team_members_routes_unauthenticated(app_url: str):
    client = AsyncClient(base_url=app_url, timeout=30.0)

    routes = [
        ("GET", "/api/v1/team-members"),
        ("POST", "/api/v1/team-members"),
        ("DELETE", "/api/v1/team-members"),
    ]

    for method, path in routes:
        response = await client.request(method, path)
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    await client.aclose()

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_teams_routes_unauthenticated(app_url: str):
    client = AsyncClient(base_url=app_url, timeout=30.0)
    team_id = uuid.uuid4()

    routes = [
        ("GET", "/api/v1/teams"),
        ("GET", f"/api/v1/teams/{team_id}"),
        ("POST", "/api/v1/teams"),
        ("PATCH", f"/api/v1/teams/{team_id}"),
        ("DELETE", f"/api/v1/teams/{team_id}"),
    ]

    for method, path in routes:
        response = await client.request(method, path)
        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    await client.aclose()

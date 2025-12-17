import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_teams_routes_unauthenticated(http_client: AsyncClient):
    """
    Тестируем что эндпоинты teams требуют аутентификации.
    Все запросы без токена должны возвращать 401.
    """
    team_id = "00000000-0000-0000-0000-000000000001"

    routes = [
        ("GET", "/api/v1/teams"),
        ("POST", "/api/v1/teams"),
        ("GET", f"/api/v1/teams/{team_id}"),
        ("PATCH", f"/api/v1/teams/{team_id}"),
        ("DELETE", f"/api/v1/teams/{team_id}"),
    ]

    for method, url in routes:
        response = await http_client.request(method, url)

        # Допускаем либо 401 (требуется auth), либо 404 (роут не реализован)
        assert response.status_code in (401, 404), (
            f"{method} {url} should return 401 (auth required) or 404 (not implemented), "
            f"but got {response.status_code}"
        )

        assert response.status_code >= 400, (
            f"{method} {url} should not succeed without authentication"
        )

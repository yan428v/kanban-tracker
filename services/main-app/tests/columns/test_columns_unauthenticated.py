import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_columns_routes_unauthenticated(http_client: AsyncClient):
    """
    Тестируем что эндпоинты columns требуют аутентификации.
    Все запросы без токена должны возвращать 401.
    """
    column_id = "00000000-0000-0000-0000-000000000001"

    routes = [
        ("GET", "/api/v1/columns"),
        ("POST", "/api/v1/columns"),
        ("GET", f"/api/v1/columns/{column_id}"),
        ("PATCH", f"/api/v1/columns/{column_id}"),
        ("DELETE", f"/api/v1/columns/{column_id}"),
    ]

    for method, url in routes:
        response = await http_client.request(method, url)

        assert response.status_code == 401, (
            f"{method} {url} should return 401 (auth required), "
            f"but got {response.status_code}"
        )

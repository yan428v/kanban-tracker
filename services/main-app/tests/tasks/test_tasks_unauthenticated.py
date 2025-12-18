import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(loop_scope="session")
async def test_tasks_routes_unauthenticated(http_client: AsyncClient):
    """
    Тестируем что эндпоинты tasks требуют аутентификации.
    Все запросы без токена должны возвращать 401.
    """
    task_id = "00000000-0000-0000-0000-000000000001"

    routes = [
        ("GET", "/api/v1/tasks"),
        ("POST", "/api/v1/tasks"),
        ("GET", f"/api/v1/tasks/{task_id}"),
        ("PATCH", f"/api/v1/tasks/{task_id}"),
        ("DELETE", f"/api/v1/tasks/{task_id}"),
    ]

    for method, url in routes:
        response = await http_client.request(method, url)

        assert response.status_code == 401, (
            f"{method} {url} should return 401 (auth required), "
            f"but got {response.status_code}"
        )

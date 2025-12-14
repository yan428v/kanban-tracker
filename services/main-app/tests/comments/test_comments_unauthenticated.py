import uuid

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_comments_routes_unauthenticated(test_client):
    comment_id = uuid.uuid4()

    routes = [
        ("GET", "/api/v1/comments/"),
        ("GET", f"/api/v1/comments/{comment_id}"),
        ("POST", "/api/v1/comments/"),
        ("PUT", f"/api/v1/comments/{comment_id}"),
        ("DELETE", f"/api/v1/comments/{comment_id}"),
    ]

    for method, path in routes:
        if method == "POST":
            response = await test_client.request(
                method,
                path,
                json={
                    "body": "test",
                    "user_id": str(uuid.uuid4()),
                    "task_id": str(uuid.uuid4()),
                },
            )
            assert response.status_code != 401
        elif method in ["PUT"]:
            response = await test_client.request(method, path, json={"body": "test"})
            assert response.status_code != 401
        else:
            response = await test_client.request(method, path)
            assert response.status_code != 401

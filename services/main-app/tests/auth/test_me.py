import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import create_access_token
from auth.security import hash_password
from models import User


class TestGetMe:
    """Тесты эндпоинта GET /api/v1/auth/me"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_success(
        self,
        default_auth_client: AsyncClient,
        default_auth_user: User,
    ):
        """Успешное получение информации о текущем пользователе."""
        response = await default_auth_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(default_auth_user.id)
        assert data["name"] == default_auth_user.name
        assert data["email"] == default_auth_user.email
        assert "created_at" in data
        assert "updated_at" in data
        # Пароль НЕ должен возвращаться
        assert "password" not in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_unauthenticated(self, http_client: AsyncClient):
        """Запрос без токена должен вернуть 401."""
        response = await http_client.get("/api/v1/auth/me")

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Not authenticated"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_invalid_token(self, http_client: AsyncClient):
        """Запрос с невалидным токеном должен вернуть 401."""
        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_expired_token(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Запрос с истёкшим токеном должен вернуть 401."""
        from datetime import datetime, timedelta

        from jose import jwt

        from core.config import auth_config

        user = User(
            name="Expired Token User",
            email="expired-token@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём токен с истёкшим сроком
        expired_payload = {
            "sub": str(user.id),
            "type": "access",
            "exp": datetime.utcnow() - timedelta(hours=1),  # Истёк час назад
        }
        expired_token = jwt.encode(
            expired_payload,
            auth_config.secret_key,
            algorithm=auth_config.algorithm,
        )

        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_deleted_user(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Запрос от удалённого пользователя должен вернуть 401."""
        user = User(
            name="To Be Deleted",
            email="deleted@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём токен
        token = create_access_token(user.id)

        # Удаляем пользователя
        await db_session.delete(user)
        await db_session.commit()

        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_nonexistent_user_id(self, http_client: AsyncClient):
        """Токен с несуществующим user_id должен вернуть 401."""
        # Создаём токен для несуществующего пользователя
        fake_user_id = uuid.uuid4()
        token = create_access_token(fake_user_id)

        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_with_refresh_token(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Запрос с refresh token вместо access должен вернуть 401."""
        from auth.jwt import create_refresh_token, generate_jti

        user = User(
            name="Refresh Token User",
            email="refresh-as-access@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio(loop_scope="session")
    async def test_get_me_malformed_authorization_header(
        self, http_client: AsyncClient
    ):
        """Запрос с неправильным форматом Authorization header."""
        # Без "Bearer" префикса
        response = await http_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "some-token"},
        )

        assert response.status_code == 401

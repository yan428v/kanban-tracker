from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import create_refresh_token, generate_jti
from auth.security import hash_password
from models import RefreshToken, User


class TestLogout:
    """Тесты эндпоинта POST /api/v1/auth/logout"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_logout_success(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Успешный logout должен отозвать refresh token."""
        user = User(
            name="Test User",
            email="logout-test@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_revoked=False,
        )
        db_session.add(token_record)
        await db_session.commit()

        # Делаем logout
        response = await http_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 204

        # Проверяем что токен отозван в БД
        result = await db_session.execute(
            select(RefreshToken).where(RefreshToken.token_jti == jti)
        )
        token_in_db = result.scalar_one()
        assert token_in_db.is_revoked is True

    @pytest.mark.asyncio(loop_scope="session")
    async def test_logout_invalid_token(self, http_client: AsyncClient):
        """Logout с невалидным токеном должен вернуть 401."""
        response = await http_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid refresh token"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_logout_already_revoked(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Logout уже отозванного токена должен работать (идемпотентность)."""
        user = User(
            name="Test User",
            email="already-revoked@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        # Сохраняем как уже отозванный
        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_revoked=True,
        )
        db_session.add(token_record)
        await db_session.commit()

        response = await http_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )

        # Должен работать без ошибки (идемпотентность)
        assert response.status_code == 204

    @pytest.mark.asyncio(loop_scope="session")
    async def test_logout_missing_token(self, http_client: AsyncClient):
        """Logout без токена должен вернуть 422."""
        response = await http_client.post(
            "/api/v1/auth/logout",
            json={},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_logout_token_not_in_db(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Logout токена, которого нет в БД, должен работать без ошибки."""
        user = User(
            name="Test User",
            email="not-in-db-logout@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём валидный JWT, но НЕ сохраняем в БД
        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        response = await http_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )

        # Logout должен быть идемпотентным - не ошибка если токена нет
        assert response.status_code == 204

    @pytest.mark.asyncio(loop_scope="session")
    async def test_cannot_use_token_after_logout(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """После logout токен не должен работать для refresh."""
        user = User(
            name="Test User",
            email="use-after-logout@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_revoked=False,
        )
        db_session.add(token_record)
        await db_session.commit()

        # Сначала делаем logout
        logout_response = await http_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )
        assert logout_response.status_code == 204

        # Пытаемся использовать токен для refresh
        refresh_response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert refresh_response.status_code == 401
        data = refresh_response.json()
        assert data["detail"] == "Refresh token has been revoked"

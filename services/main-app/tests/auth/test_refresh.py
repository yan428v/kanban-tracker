from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.jwt import create_refresh_token, generate_jti
from auth.security import hash_password
from models import RefreshToken, User


class TestRefresh:
    """Тесты эндпоинта POST /api/v1/auth/refresh"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_success(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Успешное обновление токенов."""
        # Создаём пользователя
        user = User(
            name="Test User",
            email="refresh-test@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём refresh token
        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        # Сохраняем в БД
        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_revoked=False,
        )
        db_session.add(token_record)
        await db_session.commit()

        # Делаем запрос на refresh
        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # В текущей реализации refresh_token остаётся тот же (reuse strategy)
        assert data["refresh_token"] == refresh_token

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_invalid_token(self, http_client: AsyncClient):
        """Refresh с невалидным токеном должен вернуть 401."""
        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.token.here"},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Invalid or expired refresh token"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_revoked_token(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Refresh с отозванным токеном должен вернуть 401."""
        user = User(
            name="Test User",
            email="revoked-test@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        # Сохраняем как отозванный
        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() + timedelta(days=30),
            is_revoked=True,  # Отозван!
        )
        db_session.add(token_record)
        await db_session.commit()

        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Refresh token has been revoked"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_expired_token(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Refresh с истёкшим токеном должен вернуть 401."""
        user = User(
            name="Test User",
            email="expired-test@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        # Сохраняем с истёкшим сроком
        token_record = RefreshToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=datetime.utcnow() - timedelta(days=1),  # Истёк!
            is_revoked=False,
        )
        db_session.add(token_record)
        await db_session.commit()

        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Refresh token has expired"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_token_not_in_db(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Refresh с токеном, которого нет в БД, должен вернуть 401."""
        user = User(
            name="Test User",
            email="not-in-db@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём валидный JWT, но НЕ сохраняем в БД
        jti = generate_jti()
        refresh_token = create_refresh_token(user.id, jti)

        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Refresh token not found"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_missing_token(self, http_client: AsyncClient):
        """Refresh без токена должен вернуть 422."""
        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={},
        )

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_refresh_with_access_token(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Refresh с access token вместо refresh должен вернуть 401."""
        from auth.jwt import create_access_token

        user = User(
            name="Test User",
            email="access-as-refresh@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Создаём access token (не refresh!)
        access_token = create_access_token(user.id)

        response = await http_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )

        assert response.status_code == 401

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.security import hash_password
from models import User


class TestLogin:
    """Тесты эндпоинта POST /api/v1/auth/login"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_success(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Успешный логин с правильными credentials."""
        # Создаём пользователя
        user = User(
            name="Test User",
            email="login-test@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()

        payload = {
            "email": "login-test@example.com",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_wrong_password(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Логин с неправильным паролем должен вернуть 401."""
        user = User(
            name="Test User",
            email="wrong-pass@example.com",
            hashed_password=hash_password("CorrectPass123!"),
        )
        db_session.add(user)
        await db_session.commit()

        payload = {
            "email": "wrong-pass@example.com",
            "password": "WrongPass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_nonexistent_user(self, http_client: AsyncClient):
        """Логин несуществующего пользователя должен вернуть 401."""
        payload = {
            "email": "nonexistent@example.com",
            "password": "SomePass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_invalid_email_format(self, http_client: AsyncClient):
        """Логин с невалидным форматом email должен вернуть 422."""
        payload = {
            "email": "not-an-email",
            "password": "SomePass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_missing_email(self, http_client: AsyncClient):
        """Логин без email должен вернуть 422."""
        payload = {
            "password": "SomePass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_missing_password(self, http_client: AsyncClient):
        """Логин без пароля должен вернуть 422."""
        payload = {
            "email": "test@example.com",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_empty_body(self, http_client: AsyncClient):
        """Логин с пустым телом должен вернуть 422."""
        response = await http_client.post("/api/v1/auth/login", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_login_case_sensitive_email(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Email должен быть case-insensitive (или case-sensitive - зависит от реализации)."""
        user = User(
            name="Test User",
            email="CaseSensitive@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # Пробуем логин с другим регистром
        payload = {
            "email": "casesensitive@example.com",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/login", json=payload)

        # В текущей реализации email case-sensitive, поэтому ожидаем 401
        # Если бы был case-insensitive, ожидали бы 200
        assert response.status_code == 401


class TestOAuth2Token:
    """Тесты эндпоинта POST /api/v1/auth/token (OAuth2 form)"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_oauth2_token_success(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Успешное получение токена через OAuth2 form."""
        user = User(
            name="OAuth User",
            email="oauth@example.com",
            hashed_password=hash_password("SecurePass123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # OAuth2PasswordRequestForm использует form data, не JSON
        response = await http_client.post(
            "/api/v1/auth/token",
            data={
                "username": "oauth@example.com",  # OAuth2 использует username
                "password": "SecurePass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_oauth2_token_wrong_credentials(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """OAuth2 с неправильными credentials должен вернуть 401."""
        user = User(
            name="OAuth User",
            email="oauth-wrong@example.com",
            hashed_password=hash_password("CorrectPass123!"),
        )
        db_session.add(user)
        await db_session.commit()

        response = await http_client.post(
            "/api/v1/auth/token",
            data={
                "username": "oauth-wrong@example.com",
                "password": "WrongPass123!",
            },
        )

        assert response.status_code == 401

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


class TestRegister:
    """Тесты эндпоинта POST /api/v1/auth/register"""

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_success(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Успешная регистрация нового пользователя."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()

        # Проверяем структуру ответа
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

        # Проверяем что пользователь создан в БД
        result = await db_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        # Пароль должен быть захеширован
        assert user.hashed_password != "SecurePass123!"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_duplicate_email(
        self,
        http_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Регистрация с уже существующим email должна вернуть 400."""
        # Создаём пользователя напрямую в БД
        from auth.security import hash_password

        existing_user = User(
            name="Existing User",
            email="existing@example.com",
            hashed_password=hash_password("password"),
        )
        db_session.add(existing_user)
        await db_session.commit()

        # Пытаемся зарегистрироваться с тем же email
        payload = {
            "name": "New User",
            "email": "existing@example.com",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "User with this email already exists"

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_invalid_email(self, http_client: AsyncClient):
        """Регистрация с невалидным email должна вернуть 422."""
        payload = {
            "name": "Test User",
            "email": "not-an-email",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any(error["loc"] == ["body", "email"] for error in data["detail"])

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_missing_name(self, http_client: AsyncClient):
        """Регистрация без имени должна вернуть 422."""
        payload = {
            "email": "test@example.com",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any(
            error["loc"] == ["body", "name"] and error["type"] == "missing"
            for error in data["detail"]
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_missing_email(self, http_client: AsyncClient):
        """Регистрация без email должна вернуть 422."""
        payload = {
            "name": "Test User",
            "password": "SecurePass123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any(
            error["loc"] == ["body", "email"] and error["type"] == "missing"
            for error in data["detail"]
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_missing_password(self, http_client: AsyncClient):
        """Регистрация без пароля должна вернуть 422."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert any(
            error["loc"] == ["body", "password"] and error["type"] == "missing"
            for error in data["detail"]
        )

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_empty_body(self, http_client: AsyncClient):
        """Регистрация с пустым телом должна вернуть 422."""
        response = await http_client.post("/api/v1/auth/register", json={})

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_weak_password_no_uppercase(self, http_client: AsyncClient):
        """Пароль без заглавных букв должен быть отклонён."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "weakpassword123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_weak_password_no_lowercase(self, http_client: AsyncClient):
        """Пароль без строчных букв должен быть отклонён."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "WEAKPASSWORD123!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_weak_password_no_digit(self, http_client: AsyncClient):
        """Пароль без цифр должен быть отклонён."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "WeakPassword!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_weak_password_no_special(self, http_client: AsyncClient):
        """Пароль без спецсимволов должен быть отклонён."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "WeakPassword123",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

    @pytest.mark.asyncio(loop_scope="session")
    async def test_register_weak_password_too_short(self, http_client: AsyncClient):
        """Слишком короткий пароль должен быть отклонён."""
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "Aa1!",
        }

        response = await http_client.post("/api/v1/auth/register", json=payload)

        assert response.status_code == 422

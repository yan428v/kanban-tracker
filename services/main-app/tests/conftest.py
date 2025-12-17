import os
from collections.abc import AsyncGenerator
from dataclasses import dataclass

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from auth.jwt import create_access_token
from auth.security import hash_password
from models import User

# ============================================================================
# Конфигурация тестового окружения
# ============================================================================


@dataclass
class TestSettings:
    app_url: str | None
    db_url: str
    use_external_app: bool


def load_env_settings() -> TestSettings:
    """
    Загружает настройки из переменных окружения.

    Если APP_URL задан — используется внешнее приложение (как раньше).
    Если не задан — приложение запускается in-process через ASGI.
    """
    app_url = os.environ.get("APP_URL")
    db_connection_string = os.environ.get("DB_CONNECTION_STRING")

    if app_url and db_connection_string:
        # Режим внешнего окружения (docker-compose)
        db_url = f"postgresql+asyncpg://{db_connection_string}"
        return TestSettings(
            app_url=app_url,
            db_url=db_url,
            use_external_app=True,
        )
    else:
        # Режим автоматического окружения (testcontainers)
        return TestSettings(
            app_url=None,
            db_url="",  # Будет заполнено из testcontainers
            use_external_app=False,
        )


# ============================================================================
# Testcontainers фикстуры (автоматическое окружение)
# ============================================================================


@pytest.fixture(scope="session")
def postgres_container():
    """
    Поднимает PostgreSQL контейнер для тестов.
    Используется только если APP_URL не задан.
    """
    settings = load_env_settings()

    if settings.use_external_app:
        yield None
        return

    from testcontainers.postgres import PostgresContainer

    with PostgresContainer(
        image="postgres:latest",
        username="test_user",
        password="test_password",
        dbname="test_db",
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_url(postgres_container) -> str:
    """URL для подключения к БД."""
    settings = load_env_settings()

    if settings.use_external_app:
        db_connection_string = os.environ.get("DB_CONNECTION_STRING")
        return f"postgresql+asyncpg://{db_connection_string}"

    # Получаем URL из testcontainers и конвертируем для asyncpg
    sync_url = postgres_container.get_connection_url()
    return sync_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def app_url() -> str | None:
    """URL внешнего приложения (если используется)."""
    settings = load_env_settings()
    return settings.app_url if settings.use_external_app else None


# ============================================================================
# Database фикстуры
# ============================================================================


@pytest.fixture(scope="session")
async def db_engine(db_url):
    """SQLAlchemy async engine."""
    engine = create_async_engine(db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def setup_database(db_engine, postgres_container):
    """
    Создаёт таблицы в БД.
    Для testcontainers — создаём таблицы напрямую.
    Для внешнего окружения — предполагаем что миграции уже применены.
    """
    settings = load_env_settings()

    if not settings.use_external_app:
        from models import Base

        async with db_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield


@pytest.fixture
async def db_session(db_engine, setup_database) -> AsyncGenerator[AsyncSession]:
    """Сессия БД для каждого теста."""
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.close()


# ============================================================================
# Приложение и HTTP-клиент
# ============================================================================


@pytest.fixture(scope="session")
def test_app(db_url, setup_database):
    """
    FastAPI приложение для тестов.
    Подменяет настройки БД на тестовые.
    """
    settings = load_env_settings()

    if settings.use_external_app:
        yield None
        return

    # Подменяем настройки БД перед импортом приложения
    os.environ["DB_SETTINGS__DB_HOST"] = "overridden"  # Не используется напрямую

    # Патчим database URL
    from unittest.mock import patch

    from core.config import DatabaseConfig

    with patch.object(DatabaseConfig, "url", property(lambda self: db_url)):
        from main import app

        yield app


@pytest.fixture
async def http_client(app_url, test_app) -> AsyncGenerator[AsyncClient]:
    """
    HTTP-клиент для тестов.
    Использует внешний URL или ASGI transport в зависимости от режима.
    """
    settings = load_env_settings()

    if settings.use_external_app:
        async with AsyncClient(base_url=app_url, timeout=30.0) as client:
            yield client
    else:
        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            timeout=30.0,
        ) as client:
            yield client


# ============================================================================
# Аутентификация
# ============================================================================


@pytest.fixture
async def default_auth_user(db_session: AsyncSession) -> User:
    """Создаёт пользователя для аутентифицированных тестов."""
    user = User(
        name="Default Auth User",
        email="default-auth-user@test.com",
        hashed_password=hash_password("TestPassword123!"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def default_auth_client(
    app_url,
    test_app,
    default_auth_user: User,
) -> AsyncGenerator[AsyncClient]:
    """HTTP-клиент с Bearer токеном."""
    settings = load_env_settings()
    token = create_access_token(default_auth_user.id)
    headers = {"Authorization": f"Bearer {token}"}

    if settings.use_external_app:
        async with AsyncClient(
            base_url=app_url,
            timeout=30.0,
            headers=headers,
        ) as client:
            yield client
    else:
        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            timeout=30.0,
            headers=headers,
        ) as client:
            yield client


# ============================================================================
# Cleanup
# ============================================================================


@pytest.fixture(autouse=True)
async def cleanup_db(db_session: AsyncSession):
    """Очищает все таблицы после каждого теста."""
    yield

    # Получаем список таблиц
    result = await db_session.execute(
        text("""
             SELECT tablename
             FROM pg_tables
             WHERE schemaname = 'public'
             """)
    )
    tables = [row[0] for row in result]

    # Очищаем таблицы
    for table in tables:
        await db_session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
    await db_session.commit()

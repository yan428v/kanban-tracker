import os
from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from auth.jwt import create_access_token
from auth.security import hash_password
from models import User


@dataclass
class TestSettings:
    app_url: str
    db_url: str


def load_env_settings() -> TestSettings:
    app_url = os.environ.get("APP_URL")
    if not app_url:
        raise ValueError("APP_URL environment variable is required")

    db_connection_string = os.environ.get("DB_CONNECTION_STRING")
    if not db_connection_string:
        raise ValueError("DB_CONNECTION_STRING environment variable is required")

    db_url = f"postgresql+asyncpg://{db_connection_string}"

    return TestSettings(app_url=app_url, db_url=db_url)


@pytest.fixture(scope="session")
def app_url() -> str:
    settings = load_env_settings()
    return settings.app_url


@pytest.fixture(scope="session")
def db_url() -> str:
    settings = load_env_settings()
    return settings.db_url


@pytest.fixture(scope="session")
async def db_engine(db_url):
    engine = create_async_engine(db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session = async_sessionmaker(db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.close()


@pytest.fixture
async def default_auth_user(db_session):
    user = User(
        name="Default Auth User",
        email="default-auth-user@test.com",
        hashed_password=hash_password("testpassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def create_auth_client_for_user(app_url: str, user: User) -> AsyncClient:
    token = create_access_token(user.id)
    return AsyncClient(
        base_url=app_url,
        timeout=30.0,
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.fixture
async def default_auth_client(app_url, default_auth_user):
    client = create_auth_client_for_user(app_url, default_auth_user)
    async with client:
        yield client


@pytest.fixture(autouse=True)
async def cleanup_db(db_session):
    yield
    result = await db_session.execute(
        text("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
    )
    tables = [row[0] for row in result]
    for table in tables:
        await db_session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))
    await db_session.commit()


@pytest.fixture
async def test_client(app_url):
    client = AsyncClient(base_url=app_url, timeout=30.0)
    async with client:
        yield client

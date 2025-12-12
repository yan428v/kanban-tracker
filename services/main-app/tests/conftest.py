import os
from dataclasses import dataclass

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


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
async def test_client(app_url):
    async with AsyncClient(base_url=app_url, timeout=30.0) as client:
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
        await db_session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
    await db_session.commit()

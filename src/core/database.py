from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import db_config

engine = create_async_engine(db_config.url, echo=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with async_session() as session:
        yield session

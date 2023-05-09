from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from stt.config import get_settings

DATABASE_URL = get_settings().database_url


# SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}/{PG_DB}"
async_engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": not DATABASE_URL.startswith("sqlite")},
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

Base = declarative_base()


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_clean_up_pooled_connections():
    await async_engine.dispose()


async def get_db():
    session = async_session()
    try:
        yield session
    finally:
        await session.close()

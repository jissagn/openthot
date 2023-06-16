from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from stt.config import get_settings

DATABASE_URL = get_settings().database_url


# SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}/{PG_DB}"
async_engine = create_async_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": not DATABASE_URL.startswith("sqlite")},
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


#
# Base classes
#
class SqlaBase(DeclarativeBase):
    pass


class SqlaUserBase(SQLAlchemyBaseUserTableUUID, SqlaBase):
    pass


#
# utils
#
async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SqlaBase.metadata.create_all)


async def close_clean_up_pooled_connections():
    await async_engine.dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, SqlaUserBase)  # type: ignore

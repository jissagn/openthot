import asyncio
import uuid
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import aiofiles
import pytest
import pytest_asyncio
from httpx import AsyncClient
from pydantic import EmailStr, FilePath
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from stt.api.main import app
from stt.db import schemas
from stt.db.database import DBBase, get_db
from stt.db.rw import create_interview
from stt.models.interview import InterviewCreate
from stt.models.users import UserCreate, UserRead

V1_PREFIX = "http://test.api/api/v1"


@pytest.fixture(scope="session")
def event_loop():
    """Redeclare the event_loop to force scope to 'session'."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_test_engine():
    async_test_engine = create_async_engine(
        "sqlite+aiosqlite:///./data/test.db",
        connect_args={"check_same_thread": False},
    )
    # if not database_exists:
    #     create_database(async_test_engine.url)

    async with async_test_engine.begin() as conn:
        await conn.run_sync(DBBase.metadata.create_all)
    yield async_test_engine


@pytest_asyncio.fixture(scope="function")
async def async_test_session(db_test_engine: AsyncEngine):
    connection = await db_test_engine.connect()

    # begin a non-ORM transaction
    transaction = await connection.begin()

    # bind an individual Session to the connection
    db = AsyncSession(bind=connection, expire_on_commit=False)

    yield db

    await db.close()
    await transaction.rollback()
    await connection.close()

    # async with async_test_session() as session:
    #     yield session


#
# API global fixtures
#
@pytest_asyncio.fixture(scope="function")
async def client(async_test_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: async_test_session

    async with AsyncClient(
        app=app,
        base_url=V1_PREFIX,
        follow_redirects=True,
    ) as tc:
        yield tc


@pytest_asyncio.fixture(scope="function")
async def registered_user(client: AsyncClient) -> UserCreate:
    user_create_input = UserCreate(
        email=EmailStr("test@test.com"), password="pwdtest!1"
    )
    response = await client.post("/auth/register", json=user_create_input.dict())
    if response.status_code == 201 or (
        response.status_code == 400
        and response.json()["detail"] == "REGISTER_USER_ALREADY_EXISTS"
    ):
        return user_create_input
    else:
        raise Exception("Could not register user in fixture.")


@pytest_asyncio.fixture(scope="function")
async def access_token(client: AsyncClient, registered_user) -> str:
    response = await client.post(
        "/auth/jwt/login",
        data={
            "grant_type": "password",
            "username": registered_user.email,
            "password": registered_user.password,
        },
    )
    return response.json()["access_token"]


@pytest_asyncio.fixture(scope="function")
async def logged_user(client: AsyncClient, access_token) -> UserRead:
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await client.get(
        "/users/me",
        headers=headers,
    )
    return UserRead(**response.json())


#
# DB fillings
#
@pytest_asyncio.fixture(scope="function")
async def db_interviews(async_test_session):
    user = schemas.DBUserBase(id=uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))
    for i in range(10):
        interview = InterviewCreate(name=f"Test db itw {i}")
        audio_location: FilePath = Path(f"/fake/path/audio_{i}.wav")
        await create_interview(
            async_test_session,
            user,
            interview,
            audio_location,
        )


#
# Files
#
@pytest_asyncio.fixture(scope="session")
async def upload_file_mp3() -> BinaryIO:
    async with aiofiles.open("./tests/bonjour.mp3", "rb") as mp3:
        return BytesIO(await mp3.read())

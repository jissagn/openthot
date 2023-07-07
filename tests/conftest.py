import asyncio
import contextlib
import json
import os
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import aiofiles
import pytest
import pytest_asyncio
from httpx import AsyncClient

# from polyfactory import Require
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from openthot.api.main import app
from openthot.api.v1.routers.auth import get_user_manager
from openthot.db.database import SqlaBase, SqlaUserBase, get_db
from openthot.db.rw import create_interview
from openthot.models.interview import DBInputInterviewCreate, DBInputInterviewUpdate
from openthot.models.transcript.openthot import OpenthotTranscript
from openthot.models.transcript.whisper import WhisperTranscript
from openthot.models.transcript.whisperx import WhisperXTranscript
from openthot.models.users import UserCreate, UserRead

V1_PREFIX = "http://test.api/api/v1"
MP3_FILE_PATH = Path("./tests/bonjour.mp3")
TEST_DB = "./data/test.db"


@pytest.fixture(scope="session")
def celery_config():
    return {
        "task_always_eager": True,
    }


@pytest.fixture(scope="session")
def event_loop():
    """Redeclare the event_loop to force scope to 'session'."""
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_test_engine():
    async_test_engine = create_async_engine(
        f"sqlite+aiosqlite:///{TEST_DB}",
        connect_args={"check_same_thread": False},
    )
    # if not database_exists:
    #     create_database(async_test_engine.url)

    async with async_test_engine.begin() as conn:
        await conn.run_sync(SqlaBase.metadata.create_all)
    yield async_test_engine
    os.unlink(TEST_DB)


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


@pytest_asyncio.fixture(scope="function")
async def async_user_test_session(async_test_session: AsyncSession):
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

    yield SQLAlchemyUserDatabase(async_test_session, SqlaUserBase)  # type: ignore


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
        email=EmailStr("api_user@test.com"), password="pwdtest!1"
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
    token = response.json()["access_token"]
    # print(token)
    return token


@pytest_asyncio.fixture(scope="session")
async def schemathesis_access_token(client: AsyncClient, registered_user) -> str:
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
@register_fixture
class InterviewUpdateFactory(ModelFactory[DBInputInterviewUpdate]):
    __model__ = DBInputInterviewUpdate
    __random_seed__ = 0

    audio_location = MP3_FILE_PATH


# @pytest_asyncio.fixture(scope="function")
# async def db_interviews(
#     async_test_session, interview_update_factory: InterviewUpdateFactory
# ):
#     db_interviews = []
#     for i in range(1):
#         itw_upd = interview_update_factory.build(name="whatever")
#         user = schemas.DBUserBase(id=uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))
#         interview = APIInputInterviewCreate(name=itw_upd.name)
#         db_itw = await create_interview(
#             async_test_session,
#             user,
#             interview,
#             itw_upd.audio_location, # type: ignore
#         )
#         itw_upd.id = db_itw.id
#         await update_interview(async_test_session, db_itw, itw_upd)
#         db_interviews.append(itw_upd)
#     return db_interviews

get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


@pytest_asyncio.fixture(scope="function")
async def sqla_user(async_user_test_session):
    async with get_user_manager_context(
        user_db=async_user_test_session
    ) as user_manager:
        user = await user_manager.create(
            UserCreate(email=EmailStr("db_user@test.com"), password="pwdtest!1")
        )
    return user


@pytest_asyncio.fixture(scope="function")
async def sqla_interview(async_test_session, sqla_user):
    interview = DBInputInterviewCreate(
        name="test interview",
        audio_filename="test.mp3",
        audio_location=MP3_FILE_PATH,
        audio_duration=0.1,
    )
    return await create_interview(
        async_test_session,
        sqla_user,
        interview,
    )


@pytest_asyncio.fixture(scope="function")
async def sqla_interviews(async_test_session, sqla_user):
    r = []
    for i in range(10):
        interview = DBInputInterviewCreate(
            name=f"{i} test interview",
            audio_filename=f"{i} test.mp3",
            audio_location=MP3_FILE_PATH,
            audio_duration=0.1,
        )
        r.append(
            await create_interview(
                async_test_session,
                sqla_user,
                interview,
            )
        )
    return r


#
# Files
#
@pytest_asyncio.fixture(scope="session")
async def upload_file_mp3() -> BinaryIO:
    async with aiofiles.open("./tests/bonjour.mp3", "rb") as mp3:
        return BytesIO(await mp3.read())


@pytest_asyncio.fixture(scope="session")
async def whisper_output_example1() -> WhisperTranscript:
    async with aiofiles.open("./tests/whisper.output.example1.json", "r") as json_file:
        j = await json_file.read()
        return WhisperTranscript.parse_obj(json.loads(j))


@pytest_asyncio.fixture(scope="session")
async def whisperx_output_example2() -> WhisperXTranscript:
    async with aiofiles.open("./tests/whisperx.output.example2.json", "r") as json_file:
        j = await json_file.read()
        return WhisperXTranscript.parse_obj(json.loads(j))


@pytest_asyncio.fixture(scope="session")
async def ott_simple_example1() -> OpenthotTranscript:
    async with aiofiles.open("./tests/ott_simple.example1.json", "r") as json_file:
        j = await json_file.read()
        return OpenthotTranscript.parse_obj(json.loads(j))


@pytest_asyncio.fixture(scope="session")
async def ott_simple_example2() -> OpenthotTranscript:
    async with aiofiles.open("./tests/ott_simple.example2.json", "r") as json_file:
        j = await json_file.read()
        return OpenthotTranscript.parse_obj(json.loads(j))

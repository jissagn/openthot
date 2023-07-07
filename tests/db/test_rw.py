import uuid

import pytest
from pydantic import FilePath
from pyrate_limiter import Iterable

from openthot.db.database import SqlaUserBase
from openthot.db.rw import create_interview, get_interviews
from openthot.db.schemas import SqlaInterview
from openthot.models.interview import (
    DBInputInterviewCreate,
    DBOutputInterview,
    InterviewStatus,
)
from tests.conftest import MP3_FILE_PATH


@pytest.mark.asyncio
@pytest.mark.parametrize("with_transcript", (True, False))
async def test_get_interviews(
    async_test_session, sqla_user, sqla_interviews, with_transcript
):
    result: Iterable[SqlaInterview] = await get_interviews(
        async_test_session, sqla_user, with_transcript=with_transcript
    )
    assert result is not None
    result = list(result)
    assert len(result) == len(sqla_interviews)
    for r in result:
        if not with_transcript:
            assert r.transcript_raw is None
        try:
            DBOutputInterview.from_orm(r)
        except Exception as e:
            pytest.fail(f"Cannot be parsed into DBOutputInterview pydantic model : {e}")


@pytest.mark.asyncio
async def test_create_interview_valid_input(async_test_session):
    user = SqlaUserBase(id=uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))

    audio_location: FilePath = MP3_FILE_PATH
    interview_create = DBInputInterviewCreate(
        name="Test Interview",
        audio_filename="Some filename",
        audio_location=audio_location,
        audio_duration=0.1,
    )
    result = await create_interview(async_test_session, user, interview_create)
    assert result.name == interview_create.name
    assert result.status == InterviewStatus.uploaded
    assert result.creator_id == user.id
    assert result.audio_location == str(audio_location)

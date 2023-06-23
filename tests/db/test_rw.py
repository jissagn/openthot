import uuid

import pytest
from pydantic import FilePath

from stt.db.database import SqlaUserBase
from stt.db.rw import create_interview
from stt.models.interview import DBInputInterviewCreate, InterviewStatus
from tests.conftest import MP3_FILE_PATH


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

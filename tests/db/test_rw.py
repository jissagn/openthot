from pathlib import Path
import uuid
import pytest
from pydantic import FilePath
from stt.db.database import DBUserBase

from stt.db.rw import create_interview
from stt.models.interview import APIInputInterviewCreate, InterviewStatus


@pytest.mark.asyncio
async def test_create_interview_valid_input(async_test_session):
    user = DBUserBase(id=uuid.UUID("ffffffff-ffff-ffff-ffff-ffffffffffff"))
    interview_create = APIInputInterviewCreate(name="Test Interview")
    audio_location: FilePath = Path("test_audio.mp3")
    result = await create_interview(
        async_test_session, user, interview_create, audio_location
    )
    assert result.name == interview_create.name
    assert result.status == InterviewStatus.uploaded
    assert result.creator_id == user.id
    assert result.audio_location == str(audio_location)

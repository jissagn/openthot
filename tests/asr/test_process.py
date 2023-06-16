import pytest

from stt.asr.process import process_audio
from stt.db import rw
from stt.db.schemas import SqlaInterview
from stt.models.interview import DBOutputInterview, InterviewStatus
from stt.models.transcript.whisperx import (
    WhisperXSegment,
    WhisperXTranscript,
    WhisperXWord,
)


class TestProcessAudio:
    # Tests that transcription succeeds and interview is updated accordingly
    @pytest.mark.asyncio
    async def test_transcription_success(
        self,
        mocker,
        async_test_session,
        sqla_interview: SqlaInterview,
    ):
        mock_word = WhisperXWord(
            end=None, start=None, speaker=None, word="test", score=0.5
        )
        mock_transcript = WhisperXTranscript(
            segments=[
                WhisperXSegment(
                    end=123.0,
                    start=012.3,
                    speaker="TEST SPEAKER",
                    text="Some test transcription",
                    words=[mock_word],
                )
            ],
            word_segments=[mock_word],
        )
        mock_transcriptor = mocker.AsyncMock()
        mock_transcriptor.success = True
        mock_transcriptor.transcript_duration = 10.5
        mock_transcriptor.transcript = mock_transcript
        mocker.patch(
            "stt.asr.process.transcriptor_class", return_value=mock_transcriptor
        )
        await process_audio(
            session=async_test_session,
            user_id=sqla_interview.creator_id,
            interview_id=sqla_interview.id,  # type: ignore
            audio_location=sqla_interview.audio_location,  # type: ignore
        )
        interview = await rw.get_interview(
            async_test_session,
            user=sqla_interview.creator_id,  # type: ignore
            interview_id=sqla_interview.id,  # type: ignore
        )
        assert interview is not None
        interview = DBOutputInterview.from_orm(interview)
        assert interview.status == InterviewStatus.transcripted
        assert interview.transcript_duration_s == 11
        assert interview.transcript_ts is not None
        assert interview.transcript_raw == mock_transcript

    # Tests that an exception is raised when interview is not found
    @pytest.mark.asyncio
    async def test_interview_not_found(
        self,
        mocker,
        async_test_session,
        sqla_interview: SqlaInterview,
    ):
        mocker.patch("stt.asr.process.rw.get_interview", return_value=None)
        with pytest.raises(Exception):
            await process_audio(
                session=async_test_session,
                user_id=sqla_interview.creator_id,
                interview_id=sqla_interview.id,  # type: ignore
                audio_location=sqla_interview.audio_location,  # type: ignore
            )

    # Tests that an exception is raised when transcription fails
    @pytest.mark.asyncio
    async def test_transcription_failure(
        self,
        mocker,
        async_test_session,
        sqla_interview: SqlaInterview,
    ):
        mock_transcriptor = mocker.Mock()
        mock_transcriptor.success = False
        mocker.patch(
            "stt.asr.process.transcriptor_class", return_value=mock_transcriptor
        )
        with pytest.raises(Exception):
            await process_audio(
                session=async_test_session,
                user_id=sqla_interview.creator_id,
                interview_id=sqla_interview.id,  # type: ignore
                audio_location=sqla_interview.audio_location,  # type: ignore
            )

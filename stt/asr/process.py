from datetime import datetime
from typing import Type

import structlog
from celery import Celery
from pydantic import FilePath
from sqlalchemy.ext.asyncio import AsyncSession

from stt.asr.transcriptors import Transcriptor
from stt.asr.transcriptors.whisper import Whisper
from stt.asr.transcriptors.whisperx import WhisperX
from stt.asr.transcriptors.wordcab import Wordcab
from stt.config import get_settings
from stt.db import rw
from stt.models.interview import (
    DBInputInterviewUpdate,
    InterviewId,
    InterviewStatus,
    TranscriptorSource,
)
from stt.models.users import UserId

logger = structlog.get_logger(__file__)

celery = Celery()
celery.conf.update(**get_settings().celery.dict())

transcriptors: dict[TranscriptorSource, Type[Transcriptor]] = {
    TranscriptorSource.whisper: Whisper,
    TranscriptorSource.whisperx: WhisperX,
    TranscriptorSource.wordcab: Wordcab,
}

transcriptor_source = get_settings().asr.engine
transcriptor_class = transcriptors[transcriptor_source]


async def process_audio(
    session: AsyncSession,
    user_id: UserId,
    interview_id: InterviewId,
    audio_location: FilePath,
):
    """Function to actually process the audio and
    perform transcription.
    """

    interview = await rw.get_interview(
        session=session, user=user_id, interview_id=interview_id
    )
    if interview is None:
        await logger.aexception(
            f"No interview {interview_id} (type: {type(interview_id)}) "
            + f"for user {user_id}(type: {type(user_id)})",
            user_id=user_id,
            interview_id=interview_id,
            audio_file_path=audio_location,
        )
        raise Exception  # TODO : raise appropriate exception
    await rw.update_interview(
        session=session,
        interview_db=interview,
        interview_upd=DBInputInterviewUpdate(status=InterviewStatus.processing),
    )
    await logger.ainfo(
        "Calling transcriptor",
        user_id=user_id,
        interview_id=interview_id,
        audio_file_path=audio_location,
    )
    tscr = transcriptor_class(audio_file_path=audio_location)
    await tscr.run_transcription()

    if tscr.success:
        await rw.update_interview(
            session=session,
            interview_db=interview,
            interview_upd=DBInputInterviewUpdate(
                status=InterviewStatus.transcripted,
                transcript_duration_s=int(tscr.transcript_duration) + 1,  # ⇔ ceil
                transcript_ts=datetime.utcnow(),
                transcript_raw=tscr.transcript,
                transcript_source=transcriptor_source,
            ),
        )
    else:
        await logger.aexception(
            "Could not process transcription",
            transcriptor_type=type(tscr),
            user_id=user_id,
            interview_id=interview_id,
            audio_file_path=audio_location,
        )
        raise Exception  # TODO : raise appropriate exception

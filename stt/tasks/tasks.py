from datetime import datetime
from typing import Type

import structlog
from celery import Celery
from pydantic import FilePath

from stt.asr import Transcriptor
from stt.asr.whisper import Whisper
from stt.asr.whisperx import WhisperX
from stt.config import get_settings
from stt.db import rw
from stt.db.database import async_session
from stt.models.interview import (
    DBInputInterviewUpdate,
    InterviewId,
    InterviewStatus,
    TranscriptorSource,
)
from stt.models.users import UserId
from stt.tasks import async_task

logger = structlog.get_logger(__file__)

celery = Celery()
celery.conf.update(
    broker_url=get_settings().celery_broker_url,
    result_backend=get_settings().celery_result_backend,
    task_acks_late=get_settings().celery_task_acks_late,
)

transcriptors: dict[TranscriptorSource, Type[Transcriptor]] = {
    TranscriptorSource.whisper: Whisper,
    TranscriptorSource.whisperx: WhisperX,
}


@async_task(celery, bind=True)
async def process_audio_task(
    self,
    user_id: UserId,
    interview_id: InterviewId,
    audio_location: FilePath,
    transcriptor_source: TranscriptorSource,
):
    try:
        user_id = UserId(user_id)  # type: ignore
    except Exception as e:
        raise Exception(
            f"Provided user_id ({user_id}, type: {type(user_id)}) not a valid UserId."
        ) from e
    async with async_session() as session:
        interview = await rw.get_interview(
            session=session, user=user_id, interview_id=interview_id
        )
        if interview is None:
            await logger.aexception(
                f"No interview {interview_id} (type: {type(interview_id)}) "
                + f"for user {user_id}(type: {type(user_id)})"
            )
            raise Exception  # TODO : raise appropriate exception
        await rw.update_interview(
            session=session,
            interview_db=interview,
            interview_upd=DBInputInterviewUpdate(status=InterviewStatus.processing),
        )
        await logger.ainfo(
            "Calling transcriptor",
            interview_id=interview_id,
            audio_file_path=audio_location,
        )
        tscr_class = transcriptors[transcriptor_source]
        tscr = tscr_class(audio_file_path=audio_location)
        await tscr.run_transcription()
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

import contextlib
from typing import Type

import structlog
from celery import Celery
from pydantic import FilePath

from openthot.asr.process import process_audio
from openthot.asr.transcriptors import Transcriptor
from openthot.asr.transcriptors.whisper import Whisper
from openthot.asr.transcriptors.whisperx import WhisperX
from openthot.asr.transcriptors.wordcab import Wordcab
from openthot.config import get_settings
from openthot.db.database import get_db
from openthot.models.interview import InterviewId, TranscriptorSource
from openthot.models.users import UserId
from openthot.tasks import async_task

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

get_db_context = contextlib.asynccontextmanager(get_db)


@async_task(celery, bind=True)
async def process_audio_task(
    self,
    user_id: UserId,
    interview_id: InterviewId,
    audio_location: FilePath,
):
    if not isinstance(user_id, UserId):
        try:
            user_id = UserId(user_id)
        except Exception as e:
            await logger.aexception(
                f"Provided user_id ({user_id}, type: {type(user_id)}) not a valid UserId.",
                user_id=user_id,
                interview_id=interview_id,
                audio_file_path=audio_location,
            )
            raise Exception from e
    try:
        async with get_db_context() as async_session:
            await process_audio(
                session=async_session,
                user_id=user_id,
                interview_id=interview_id,
                audio_location=audio_location,
            )
    except Exception as e:
        await logger.aexception("Task encountered exception", exception=str(e))
        self.retry(countdown=1)

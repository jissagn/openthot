import json
from datetime import datetime

import structlog
from celery import Celery
from pydantic import FilePath

from stt.asr.transcription import run_transcription
from stt.config import get_settings
from stt.db import rw
from stt.db.database import async_session
from stt.models.interview import InterviewId, InterviewInDBBaseUpdate, InterviewStatus
from stt.models.users import UserId
from stt.tasks import async_task

logger = structlog.get_logger(__file__)

celery = Celery()
celery.conf.update(
    broker_url=get_settings().celery_broker_url,
    result_backend=get_settings().celery_result_backend,
    task_acks_late=get_settings().celery_task_acks_late,
)


@async_task(celery, bind=True)
async def process_audio_task(
    self, user_id: UserId, interview_id: InterviewId, audio_location: FilePath
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
            logger.exception(
                f"No interview {interview_id} (type: {type(interview_id)}) "
                + f"for user {user_id}(type: {type(user_id)})"
            )
            raise Exception  # TODO : raise appropriate exception
        await rw.update_interview(
            session=session,
            interview_db=interview,
            interview_upd=InterviewInDBBaseUpdate(status=InterviewStatus.processing),
        )
        logger.info(
            "Calling transcriptor",
            interview_id=interview_id,
            audio_file_path=audio_location,
        )
        json_transcript, transcript, duration = run_transcription(
            audio_file_path=audio_location
        )

        await rw.update_interview(
            session=session,
            interview_db=interview,
            interview_upd=InterviewInDBBaseUpdate(
                status=InterviewStatus.transcripted,
                transcript_duration_s=int(duration) + 1,  # ceil
                transcript_ts=datetime.utcnow(),
                transcript=json.dumps(json_transcript),
                transcript_withtimecode=transcript,
            ),
        )

import json
from datetime import datetime

from celery import Celery
from pydantic import FilePath

from stt.asr.transcription import run_transcription
from stt.config import get_settings
from stt.db import rw
from stt.db.database import Base, engine
from stt.models.interview import InterviewInDBBaseUpdate, InterviewStatus
from stt.tasks import SqlAlchemyTask

Base.metadata.create_all(bind=engine)

celery = Celery()
celery.conf.update(
    broker_url=get_settings().celery_broker_url,
    result_backend=get_settings().celery_result_backend,
    task_acks_late=get_settings().celery_task_acks_late,
)


@celery.task(bind=True, base=SqlAlchemyTask)
def process_audio_task(self, interview_id: int, audio_location: FilePath):
    interview = rw.get_interview(db=self.db, interview_id=interview_id)
    rw.update_interview(
        db=self.db,
        interview_db=interview,
        interview_upd=InterviewInDBBaseUpdate(status=InterviewStatus.processing),
    )
    json_transcript, transcript, duration = run_transcription(
        audio_file_path=audio_location
    )

    rw.update_interview(
        db=self.db,
        interview_db=interview,
        interview_upd=InterviewInDBBaseUpdate(
            status=InterviewStatus.transcripted,
            transcript_duration_s=int(duration) + 1,
            transcript_ts=datetime.utcnow(),
            transcript=json.dumps(json_transcript),
            transcript_withtimecode=transcript,
        ),
    )

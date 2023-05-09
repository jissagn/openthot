from datetime import datetime

from fastapi.encoders import jsonable_encoder
from pydantic import FilePath
from sqlalchemy.orm import Session

from stt.db import schemas
from stt.models.interview import (
    InterviewCreate,
    InterviewInDBBaseUpdate,
    InterviewUpdate,
)


def create_interview(
    db: Session, interview: InterviewCreate, audio_location: FilePath
) -> schemas.DBInterview:
    db_interview = schemas.DBInterview(**interview.dict())
    db_interview.audio_location = str(audio_location)  # type: ignore
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview


def get_interview(db: Session, interview_id: int) -> schemas.DBInterview:
    return (
        db.query(schemas.DBInterview)
        .filter(schemas.DBInterview.id == interview_id)
        .first()
    )


def get_interviews(db: Session) -> list[schemas.DBInterview]:
    interviews = db.query(schemas.DBInterview).all()
    return interviews or []


def update_interview(
    db: Session,
    interview_db: schemas.DBInterview,
    interview_upd: InterviewUpdate | InterviewInDBBaseUpdate | dict,
):
    target_data = jsonable_encoder(interview_db)
    if not isinstance(interview_upd, dict):
        update_data = interview_upd.dict(exclude_unset=True)
    else:
        update_data = interview_upd
    for field in target_data:
        if field in update_data:
            if field == interview_db.update_ts:
                w = f"Required {field} to be set to {update_data[field]}, but will be overwritten."
                print("WARNING. " + w)  # TODO : use logger
            else:
                setattr(interview_db, field, update_data[field])
    interview_db.update_ts = datetime.utcnow()  # type: ignore
    db.add(interview_db)
    db.commit()
    db.refresh(interview_db)
    return interview_db

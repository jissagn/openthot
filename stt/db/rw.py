from datetime import datetime
from typing import Iterable

import structlog
from fastapi.encoders import jsonable_encoder
from pydantic import FilePath
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from stt.db import schemas
from stt.models.interview import (
    InterviewCreate,
    InterviewInDBBaseUpdate,
    InterviewUpdate,
)

logger = structlog.get_logger(__file__)


async def create_interview(
    session: AsyncSession, interview: InterviewCreate, audio_location: FilePath
) -> schemas.DBInterview:
    db_interview = schemas.DBInterview(**interview.dict())
    db_interview.audio_location = str(audio_location)  # type: ignore
    session.add(db_interview)
    await session.commit()
    await session.refresh(db_interview)
    return db_interview


async def delete_interview(session: AsyncSession, interview_id: int):
    interview = await session.get(schemas.DBInterview, interview_id)
    await session.delete(interview)
    await session.commit()


async def get_interview(
    session: AsyncSession, interview_id: int
) -> schemas.DBInterview | None:
    return await session.get(schemas.DBInterview, interview_id)


async def get_interviews(session: AsyncSession) -> Iterable[schemas.DBInterview]:
    statement = select(schemas.DBInterview)
    interviews = (await session.scalars(statement)).all()
    return interviews or []


async def update_interview(
    session: AsyncSession,
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
                logger.warn(
                    w,
                    interview_db=jsonable_encoder(interview_db),
                    interview_upd=update_data,
                )
            else:
                setattr(interview_db, field, update_data[field])
    interview_db.update_ts = datetime.utcnow()  # type: ignore
    session.add(interview_db)
    await session.commit()
    await session.refresh(interview_db)
    return interview_db

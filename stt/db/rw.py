from datetime import datetime
from typing import Iterable

import structlog
from fastapi.encoders import jsonable_encoder
from pydantic import FilePath
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from stt.db.schemas import DBInterview, DBUserBase
from stt.models.interview import (
    InterviewCreate,
    InterviewId,
    InterviewInDBBaseUpdate,
    InterviewUpdate,
)
from stt.models.users import UserId

logger = structlog.get_logger(__file__)


async def create_interview(
    session: AsyncSession,
    user: DBUserBase,
    interview: InterviewCreate,
    audio_location: FilePath,
) -> DBInterview:
    db_interview = DBInterview(**interview.dict())
    db_interview.creator_id = user.id
    db_interview.audio_location = str(audio_location)
    session.add(db_interview)
    await session.commit()
    await session.refresh(db_interview)
    return db_interview


async def delete_interview(
    session: AsyncSession, user: DBUserBase, interview_id: InterviewId
):
    interview = await get_interview(session, user, interview_id)
    await session.delete(interview)
    await session.commit()


async def get_interview(
    session: AsyncSession, user: DBUserBase | UserId, interview_id: InterviewId
) -> DBInterview | None:
    interview = await session.get(DBInterview, interview_id)
    if interview:
        if isinstance(user, UserId) and interview.creator_id == user:
            return interview
        elif isinstance(user, DBUserBase) and interview.creator_id == user.id:
            return interview
    return None


async def get_interviews(
    session: AsyncSession, user: DBUserBase
) -> Iterable[DBInterview]:
    statement = select(DBInterview).where(DBInterview.creator == user)
    interviews = (await session.scalars(statement)).all()
    return interviews or []


async def update_interview(
    session: AsyncSession,
    interview_db: DBInterview,
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
    interview_db.update_ts = datetime.utcnow()
    session.add(interview_db)
    await session.commit()
    await session.refresh(interview_db)
    return interview_db

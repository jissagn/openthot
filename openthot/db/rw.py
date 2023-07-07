import json
from collections.abc import Sequence
from datetime import datetime

import structlog
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from openthot.db.schemas import SqlaInterview, SqlaUserBase
from openthot.models.interview import (
    DBInputInterviewCreate,
    DBInputInterviewUpdate,
    InterviewId,
    InterviewSpeakers,
)
from openthot.models.users import UserId

logger = structlog.get_logger(__file__)


async def create_interview(
    session: AsyncSession,
    user: SqlaUserBase,
    interview: DBInputInterviewCreate,
) -> SqlaInterview:
    db_interview = SqlaInterview(**interview.dict())
    db_interview.audio_location = str(db_interview.audio_location)
    db_interview.creator_id = user.id
    session.add(db_interview)
    await session.commit()
    await session.refresh(db_interview)
    return db_interview


async def delete_interview(
    session: AsyncSession, user: SqlaUserBase, interview_id: InterviewId
):
    interview = await get_interview(session, user, interview_id)
    if interview is None:
        return False
    await session.delete(interview)
    await session.commit()
    return True


async def get_interview(
    session: AsyncSession,
    user: SqlaUserBase | UserId,
    interview_id: InterviewId,
) -> SqlaInterview | None:
    creator_id = None
    if isinstance(user, UserId):
        creator_id = user
    elif isinstance(user, SqlaUserBase):
        creator_id = user.id
    else:
        raise TypeError(f"`user` is type {type(user)}")
    interview = await session.scalar(
        select(SqlaInterview)
        .where(SqlaInterview.id == interview_id)
        .where(SqlaInterview.creator_id == creator_id)
    )
    return interview


async def get_interviews(
    session: AsyncSession,
    user: SqlaUserBase,
    with_transcript: bool = False,
) -> Sequence[SqlaInterview]:
    if with_transcript:
        statement = select(SqlaInterview).where(SqlaInterview.creator == user)
        interviews = (await session.scalars(statement)).all()
        return interviews
    else:
        select_stm = [
            getattr(SqlaInterview, col.key)
            for col in SqlaInterview.__table__.columns
            if col.key != "transcript_raw"
        ]

        statement = select(*select_stm).where(SqlaInterview.creator == user)
        interviews = (await session.execute(statement)).yield_per(1)
        return [SqlaInterview(**i._asdict()) for i in interviews]


async def update_interview(
    session: AsyncSession,
    interview_db: SqlaInterview,
    interview_upd: DBInputInterviewUpdate,
):
    target_data = jsonable_encoder(interview_db)
    update_data = interview_upd.dict(exclude_unset=True)
    for field in target_data:
        if field in update_data:
            if field == "update_ts":
                w = f"Received {field} to be set to {update_data[field]}, but will be overwritten."
                logger.warn(
                    w,
                    interview_db=jsonable_encoder(interview_db),
                    interview_upd=update_data,
                )
            elif field == "audio_location":
                setattr(interview_db, field, str(update_data[field]))
            elif field == "speakers":
                if raw_current_value := getattr(interview_db, field):
                    current_value: InterviewSpeakers = (
                        json.loads(raw_current_value) or {}
                    )  # type: ignore
                else:
                    current_value: InterviewSpeakers = {}
                set_value: InterviewSpeakers = update_data[field] or {}  # type: ignore
                future_value = current_value | set_value if set_value else None
                setattr(
                    interview_db,
                    field,
                    json.dumps(future_value),
                )

            elif field == "transcript_raw":
                setattr(interview_db, field, json.dumps(update_data[field]))
            else:
                setattr(interview_db, field, update_data[field])
    interview_db.update_ts = datetime.utcnow()
    session.add(interview_db)
    await session.commit()
    await session.refresh(interview_db)
    return interview_db

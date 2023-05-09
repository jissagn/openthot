import uuid

import fastapi_users as fau
from sqlalchemy import Column, DateTime, Integer, String, Text, func

from stt.db.database import Base
from stt.models.interview import InterviewStatus


class DBInterview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    audio_location = Column(String, nullable=False)
    name = Column(String, nullable=False, unique=True)
    status = Column(
        String, nullable=True, default=InterviewStatus.uploaded
    )  # TODO : only valid interview status
    transcript = Column(Text, nullable=True)
    transcript_duration_s = Column(Integer, nullable=True)
    transcript_ts = Column(DateTime(timezone=True), nullable=True)
    transcript_withtimecode = Column(Text, nullable=True)
    update_ts = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    upload_ts = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class UserRead(fau.schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(fau.schemas.BaseUserCreate):
    pass


class UserUpdate(fau.schemas.BaseUserUpdate):
    pass

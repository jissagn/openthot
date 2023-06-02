import datetime
import uuid

from fastapi_users_db_sqlalchemy.generics import GUID
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from stt.db.database import DBBase, DBUserBase
from stt.models.interview import InterviewStatus


class DBInterview(DBBase):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    audio_location: Mapped[str] = mapped_column(String, nullable=False)
    audio_filename: Mapped[str] = mapped_column(String, nullable=False)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        GUID, ForeignKey("user.id", ondelete="cascade"), nullable=False
    )  # creator_id = Column(uuid.UUID, ForeignKey("users.id"))
    creator: Mapped["DBUser"] = relationship("DBUser", back_populates="interviews")
    name: Mapped[str] = mapped_column(String, nullable=False, unique=False)
    status: Mapped[InterviewStatus] = mapped_column(
        String, nullable=False, default=InterviewStatus.uploaded
    )  # TODO : only valid interview status
    transcript_source: Mapped[str] = mapped_column(String, nullable=True)
    transcript_raw: Mapped[str] = mapped_column(Text, nullable=True)
    transcript_duration_s: Mapped[int] = mapped_column(Integer, nullable=True)
    transcript_ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transcript_withtimecode: Mapped[str] = mapped_column(Text, nullable=True)
    update_ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    upload_ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class DBUser(DBUserBase):
    interviews: Mapped[list["DBInterview"]] = relationship(
        "DBInterview", lazy="joined", back_populates="creator"
    )

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, FilePath


class InterviewStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    transcripted = "transcripted"


# Shared properties
class InterviewBase(BaseModel):
    """
    Class to represent an interview
    """

    name: str


# Properties to receive on Interview creation
class InterviewCreate(InterviewBase):
    pass


# Properties to receive on Interview update
class InterviewUpdate(InterviewBase):
    pass


# Properties shared by models stored in DB
class InterviewInDBBase(InterviewBase):
    audio_location: FilePath
    id: int
    name: str
    status: str
    transcript: str | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: str | None = None
    update_ts: datetime
    upload_ts: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class Interview(InterviewInDBBase):
    pass


# Properties properties stored in DB
class InterviewInDB(InterviewInDBBase):
    pass


class InterviewInDBBaseUpdate(InterviewBase):
    audio_location: FilePath | None = None
    id: int | None = None
    name: str | None = None
    status: str | None = None
    transcript: str | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: str | None = None
    upload_ts: datetime | None = None

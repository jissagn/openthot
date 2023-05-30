from datetime import datetime
from enum import Enum

from pydantic import BaseModel, FilePath

from stt.models.users import UserId

InterviewId = int


class InterviewStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    transcripted = "transcripted"


class _APIInputInterviewBase(BaseModel):
    """
    Class to represent common properties on expected interviews
    """

    name: str


class _InterviewInDBBase(BaseModel):
    """
    Shared properties in models used by DB
    """

    creator_id: UserId
    id: InterviewId
    name: str
    status: InterviewStatus
    transcript: str | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: str | None = None
    update_ts: datetime
    upload_ts: datetime

    class Config:
        orm_mode = True


class APIInputInterviewCreate(_APIInputInterviewBase):
    """
    Properties to receive on Interview creation.
    Actual binary audio file in not handled in body but in form data,
    therefore it is not present in this class.
    """

    pass


class APIInputInterviewUpdate(_APIInputInterviewBase):
    """
    Properties to receive on Interview update
    """

    pass


class APIOutputInterview(_InterviewInDBBase):
    """
    Properties to return to client.

    """

    pass


class InterviewUpdate(BaseModel):
    """
    Basically a class where all fields are options.
    """

    audio_location: FilePath | None = None
    creator_id: UserId | None = None
    id: InterviewId | None = None
    name: str | None = None
    status: InterviewStatus | None = None
    transcript: str | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: str | None = None
    upload_ts: datetime | None = None

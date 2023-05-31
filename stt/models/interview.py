import json
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, FilePath, validator

from stt.models.transcript import (
    SttSimpleTranscript,
    WhisperTranscript,
    wt2sttimple,
)
from stt.models.users import UserId

InterviewId = int


class InterviewStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    transcripted = "transcripted"


class TimecodedLine(BaseModel):
    tc: str
    txt: str


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
    transcript: WhisperTranscript | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: list[TimecodedLine] | None = None
    update_ts: datetime
    upload_ts: datetime

    @validator("transcript", pre=True)
    def load_transcript(cls, v):
        if not v:
            return None
        elif isinstance(v, WhisperTranscript):
            return v
        elif isinstance(v, str):
            return WhisperTranscript.parse_obj(json.loads(v))

    @validator("transcript_withtimecode", pre=True)
    def load_transcript_withtimecode(cls, v):
        if not v:
            return None
        if v:
            for s in v.split("\n"):
                t = s.split("] ")
                if len(t) < 2:
                    continue
                yield TimecodedLine(tc=t[0] + "]", txt=t[1])

    class Config:
        orm_mode = True


class APIInputInterviewCreate(_APIInputInterviewBase):
    """
    Properties to receive on Interview creation.
    Actual binary audio file in not handled in body but in
    form data, therefore it is not present in this class.
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

    transcript_simple: SttSimpleTranscript | None
    # TODO: also return original audio filename.ext

    @validator("transcript_simple", always=True)
    def load_transcript_simple(cls, v, values):
        if t := values.get("transcript"):
            s = wt2sttimple(t)
            values["transcript"] = None
            return s
        return None


class InterviewUpdate(BaseModel):
    """
    Basically a class where all fields are options
    to their corresponding DB field.
    `update_ts` is absent and left to be set by the db updating function
    """

    audio_location: FilePath | None = None
    creator_id: UserId | None = None
    id: InterviewId | None = None
    name: str | None = None
    status: InterviewStatus | None = None
    transcript: WhisperTranscript | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    transcript_withtimecode: str | None = None
    upload_ts: datetime | None = None

import json
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, FilePath, validator

from stt.models.transcript import TranscriptorSource
from stt.models.transcript.stt import SttTranscript
from stt.models.transcript.utils import wt2stt, wtx2stt
from stt.models.transcript.whisper import WhisperTranscript
from stt.models.transcript.whisperx import WhisperXTranscript
from stt.models.users import UserId

InterviewId = int
InterviewSpeakers = dict[str, str]


class InterviewStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    transcripted = "transcripted"


# Generic input/output Pydantic models here :
# - 'API*' are related to API data exchanges
# - 'DB*'  are for objects interfacing the SqlAlchemy schemas
#
#  Usage:
#  APIInputCreate --> DBInputCreate --> Sqla schema
#  APIInputUpdate --> DBInputUpdate --> Sqla schema
#  APIOuput       <-- DBOutput      <-- Sqla schema
#
# - Why do we need a DBInputCreate ?
#   Because the DB might require non-nullable fields that the
#   API user is not required to provide. E.g. `audio_location`
#
# - Why do we need a DBInputUpdate ?
#   Because the DB can update fields that the API user is not
#   allowed to update itself. E.g. `transcript_raw`
#
# - Why do we need a DBOutput model ?
#   - Because the DB has fields that we do not want to expose
#     to the API user. E.g. `audio_location`.
#   - Because the API might want to return fiels that are not
#     in the DB. E.g. `transcript`


class APIInputInterviewCreate(BaseModel):
    """
    Properties to receive on Interview creation.
    Actual binary audio file in not handled in body but in
    form data, therefore it is not present in this class.
    """

    name: str | None = None


class APIInputInterviewUpdate(BaseModel):
    """
    Properties to receive on Interview update.
    """

    name: str | None = None
    speakers: InterviewSpeakers | None = None

    @validator("name")
    def load_name(cls, v):
        if v is None:
            raise ValueError("cannot be updated to a null value")
        return v


class APIOutputInterview(BaseModel):
    """
    Properties to return to client.

    """

    audio_filename: str
    creator_id: UserId
    id: InterviewId
    name: str
    speakers: InterviewSpeakers | None = None
    status: InterviewStatus
    transcript: SttTranscript | None = None
    transcript_source: TranscriptorSource | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    update_ts: datetime
    upload_ts: datetime

    @validator("speakers")
    def load_speakers(cls, v):
        # Enforce {} to None
        return v if v else None

    @classmethod
    def from_orm(cls, obj):  # obj is an sqla schema object
        """
        We first need to parse the db schema object through
        a `DBOutputInterview`, then we can parse it to read
        `transcript_raw` et set `transcript`.
        """
        db = DBOutputInterview.from_orm(obj)
        r = super().from_orm(db)
        if tr := db.transcript_raw:
            if isinstance(tr, WhisperTranscript):
                r.transcript = wt2stt(tr)
            elif isinstance(tr, WhisperXTranscript):
                r.transcript = wtx2stt(tr)
        return r

    class Config:
        orm_mode = True


class DBInputInterviewCreate(BaseModel):
    """
    Class to represent an input (create or update) for db.
    Basically a list a all mandatory (ie non-null) fields.
    """

    name: str
    audio_filename: str
    audio_location: FilePath


class DBInputInterviewUpdate(BaseModel):
    """
    Basically a class where all fields are options
    to their corresponding DB field.
    `update_ts` is absent and left to be set by the db itself
    """

    audio_filename: str | None = None
    audio_location: FilePath | None = None
    id: InterviewId | None = None
    name: str | None = None
    speakers: InterviewSpeakers | None = None
    status: InterviewStatus | None = None
    transcript_source: TranscriptorSource | None = None
    transcript_raw: WhisperTranscript | WhisperXTranscript | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None


class DBOutputInterview(BaseModel):
    """
    Properties of DB
    """

    audio_filename: str
    audio_location: FilePath
    creator_id: UserId
    id: InterviewId
    name: str
    speakers: InterviewSpeakers | None = None
    status: InterviewStatus
    transcript_source: TranscriptorSource | None = None
    transcript_raw: WhisperTranscript | WhisperXTranscript | None = None
    transcript_duration_s: int | None = None
    transcript_ts: datetime | None = None
    update_ts: datetime
    upload_ts: datetime

    @validator("speakers", pre=True)
    def load_speakers(cls, v):
        if not v:
            return None
        else:
            return json.loads(v)

    @validator("transcript_raw", pre=True)
    def load_transcript_raw(cls, v, values):
        if not v:
            return None
        elif isinstance(v, WhisperTranscript) or isinstance(v, WhisperXTranscript):
            return v
        elif isinstance(v, str):
            transcript_source = values["transcript_source"]
            if transcript_source == TranscriptorSource.whisper:
                return WhisperTranscript.parse_obj(json.loads(v))
            elif transcript_source == TranscriptorSource.whisperx:
                return WhisperXTranscript.parse_obj(json.loads(v))

    class Config:
        orm_mode = True

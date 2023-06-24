from pydantic import BaseModel

from . import LanguageType, ProbabilityType


#
# Home-made transcript
#
class SttWord(BaseModel):
    word: str
    start: float
    probability: ProbabilityType  # type: ignore
    end: float

    class Config:
        validate_assignment = True


class SttSegment(BaseModel):
    id: int
    start: float
    end: float
    words: list[SttWord]
    speaker: str | None = None


class SttTranscript(BaseModel):
    language: LanguageType | None = None  # type: ignore
    text: str
    segments: list[SttSegment]
    speakers: set[str]

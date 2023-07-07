from pydantic import BaseModel

from . import LanguageType, ProbabilityType


#
# Home-made transcript
#
class OpenthotWord(BaseModel):
    word: str
    start: float
    probability: ProbabilityType  # type: ignore
    end: float

    class Config:
        validate_assignment = True


class OpenthotSegment(BaseModel):
    id: int
    start: float
    end: float
    words: list[OpenthotWord]
    speaker: str | None = None


class OpenthotTranscript(BaseModel):
    language: LanguageType | None = None  # type: ignore
    text: str
    segments: list[OpenthotSegment]
    speakers: set[str]

from pydantic import BaseModel
from . import ProbabilityType, LanguageType


#
# Home-made related
#
class SttSimpleWord(BaseModel):
    word: str
    start: float
    probability: ProbabilityType  # type: ignore
    end: float

    class Config:
        validate_assignment = True


class SttSimpleSegment(BaseModel):
    id: int
    start: float
    end: float
    words: list[SttSimpleWord]


class SttSimpleTranscript(BaseModel):
    language: LanguageType  # type: ignore
    text: str
    segments: list[SttSimpleSegment]

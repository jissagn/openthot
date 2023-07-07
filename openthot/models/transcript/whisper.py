from pydantic import BaseModel, confloat

from . import LanguageType, ProbabilityType


#
# Whisper-related
#
class WhisperWord(BaseModel):
    word: str
    start: float
    probability: ProbabilityType  # type: ignore
    end: float

    class Config:
        validate_assignment = True


class WhisperSegment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: list[int]
    temperature: float
    avg_logprob: confloat(le=1.0)  # type: ignore
    compression_ratio: float
    no_speech_prob: ProbabilityType  # type: ignore
    words: list[WhisperWord]

    class Config:
        validate_assignment = True


class WhisperTranscript(BaseModel):
    language: LanguageType  # type: ignore
    text: str
    segments: list[WhisperSegment]

    class Config:
        validate_assignment = True

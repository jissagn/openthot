from pydantic import BaseModel

from . import LanguageType, ProbabilityType


#
# Wordcab-transcribe related
#
class WordcabWord(BaseModel):
    end: float | None
    score: ProbabilityType | None  # type: ignore
    start: float | None
    word: str


class WordcabSegment(BaseModel):
    start: float
    end: float
    text: str
    speaker: int | None
    words: list[WordcabWord]

    class Config:
        validate_assignment = True


class WordcabTranscript(BaseModel):
    """Base response model, not meant to be used directly."""

    utterances: list[WordcabSegment]
    alignment: bool
    diarization: bool
    source_lang: LanguageType  # type: ignore
    timestamps: str
    use_batch: bool
    word_timestamps: bool

    dual_channel: bool

from pydantic import BaseModel


#
# WhisperX-related
#
class WhisperXWord(BaseModel):
    end: float | None
    score: float | None
    start: float | None
    word: str
    speaker: str | None


class WhisperXSegment(BaseModel):
    end: float
    speaker: str | None
    start: float
    text: str
    words: list[WhisperXWord]


class WhisperXTranscript(BaseModel):
    segments: list[WhisperXSegment]
    word_segments: list[WhisperXWord]

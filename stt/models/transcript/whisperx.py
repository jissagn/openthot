from pydantic import BaseModel


#
# WhisperX-related
#
class WhisperXWord(BaseModel):
    end: float
    score: float
    start: float
    word: str
    speaker: str


class WhisperXSegment(BaseModel):
    end: float
    speaker: str
    start: float
    text: str
    words: list[WhisperXWord]


class WhisperXWordSegment(BaseModel):
    end: float
    score: float
    start: float
    word: str
    speaker: str


class WhisperXTranscript(BaseModel):
    segments: list[WhisperXSegment]
    word_segments: list[WhisperXWordSegment]

from pydantic import BaseModel, confloat, constr

ProbabilityType = confloat(ge=0.0, le=1.0)
LanguageType = constr(regex=r"^(fr|en)$")


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


#
# Home-made related
#
class SttSimpleSegment(BaseModel):
    id: int
    start: float
    end: float
    words: list[WhisperWord]


class SttSimpleTranscript(BaseModel):
    language: LanguageType  # type: ignore
    text: str
    segments: list[SttSimpleSegment]


#
# Utils
#
def wt2sttimple(wt: WhisperTranscript) -> SttSimpleTranscript:
    stt_simple = SttSimpleTranscript(language=wt.language, text=wt.text, segments=[])
    for wt_segment in wt.segments:
        st_segment = SttSimpleSegment(
            id=wt_segment.id, start=wt_segment.start, end=wt_segment.end, words=[]
        )
        # avg_prob = math.exp(wt_segment.avg_logprob)
        for wt_word in wt_segment.words:
            st_word = wt_word.copy()
            # st_word.probability
            st_segment.words.append(st_word)
        stt_simple.segments.append(st_segment)
    return stt_simple

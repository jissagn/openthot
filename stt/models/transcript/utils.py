from stt.models.transcript.sttsimple import (
    SttSimpleSegment,
    SttSimpleTranscript,
    SttSimpleWord,
)
from stt.models.transcript.whisper import WhisperTranscript


def wt2sttimple(wt: WhisperTranscript) -> SttSimpleTranscript:
    stt_simple = SttSimpleTranscript(language=wt.language, text=wt.text, segments=[])
    for wt_segment in wt.segments:
        st_segment = SttSimpleSegment(
            id=wt_segment.id, start=wt_segment.start, end=wt_segment.end, words=[]
        )
        # avg_prob = math.exp(wt_segment.avg_logprob)
        for wt_word in wt_segment.words:
            st_word = SttSimpleWord(**wt_word.dict())
            # st_word.probability
            st_segment.words.append(st_word)
        stt_simple.segments.append(st_segment)
    return stt_simple

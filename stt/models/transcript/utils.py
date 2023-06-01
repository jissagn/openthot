from stt.models.transcript.stt import SttSegment, SttTranscript, SttWord
from stt.models.transcript.whisper import WhisperTranscript


def wt2stt(wt: WhisperTranscript) -> SttTranscript:
    stt = SttTranscript(language=wt.language, text=wt.text, segments=[])
    for wts in wt.segments:
        stts = SttSegment(id=wts.id, start=wts.start, end=wts.end, words=[])
        for wtw in wts.words:
            sttw = SttWord(**wtw.dict())
            stts.words.append(sttw)
        stt.segments.append(stts)
    return stt

        )
        # avg_prob = math.exp(wt_segment.avg_logprob)
        for wt_word in wt_segment.words:
            st_word = SttSimpleWord(**wt_word.dict())
            # st_word.probability
            st_segment.words.append(st_word)
        stt_simple.segments.append(st_segment)
    return stt_simple

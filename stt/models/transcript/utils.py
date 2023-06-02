from stt.models.transcript.stt import SttSegment, SttTranscript, SttWord
from stt.models.transcript.whisper import WhisperTranscript
from stt.models.transcript.whisperx import WhisperXTranscript


def wt2stt(wt: WhisperTranscript) -> SttTranscript:
    stt = SttTranscript(language=wt.language, text=wt.text, segments=[])
    for wts in wt.segments:
        stts = SttSegment(id=wts.id, start=wts.start, end=wts.end, words=[])
        for wtw in wts.words:
            sttw = SttWord(**wtw.dict())
            stts.words.append(sttw)
        stt.segments.append(stts)
    return stt


def wtx2stt(wxt: WhisperXTranscript) -> SttTranscript:
    stt = SttTranscript(language=None, text="", segments=[])
    for i, wxs in enumerate(wxt.segments):
        stts = SttSegment(
            id=i, start=wxs.start, end=wxs.end, words=[], speaker=wxs.speaker
        )
        for wxw in wxs.words:
            sttw = SttWord(**wxw.dict())
            sttw.probability = wxw.score
            stts.words.append(sttw)
        stt.segments.append(stts)
    return stt

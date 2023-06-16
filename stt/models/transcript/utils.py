from stt.models.transcript.stt import SttSegment, SttTranscript, SttWord
from stt.models.transcript.whisper import WhisperTranscript
from stt.models.transcript.whisperx import WhisperXTranscript, WhisperXWord


def wt2stt(wt: WhisperTranscript) -> SttTranscript:
    stt = SttTranscript(language=wt.language, text=wt.text, segments=[])
    for wt_seg in wt.segments:
        stts = SttSegment(id=wt_seg.id, start=wt_seg.start, end=wt_seg.end, words=[])
        for wt_word in wt_seg.words:
            sttw = SttWord(**wt_word.dict())
            stts.words.append(sttw)
        stt.segments.append(stts)
    return stt


def wtx2stt(wxt: WhisperXTranscript) -> SttTranscript:
    stt = SttTranscript(language=None, text="", segments=[])
    prev_word = WhisperXWord(
        word="", start=0.0, end=0.0, score=1.0, speaker=None
    ).dict()
    for i, wxt_seg in enumerate(wxt.segments):
        stts = SttSegment(
            id=i,
            start=wxt_seg.start,
            end=wxt_seg.end,
            words=[],
            speaker=wxt_seg.speaker,
        )
        for wxt_word in wxt_seg.words:
            # fill none fields with previous word fields
            w_dict = prev_word | wxt_word.dict(exclude_none=True)
            sttw = SttWord(**w_dict, probability=w_dict["score"])
            prev_word = w_dict
            stts.words.append(sttw)
        stt.segments.append(stts)
    return stt

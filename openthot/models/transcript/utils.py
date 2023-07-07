from openthot.models.transcript.openthot import (
    OpenthotSegment,
    OpenthotTranscript,
    OpenthotWord,
)
from openthot.models.transcript.whisper import WhisperTranscript
from openthot.models.transcript.whisperx import WhisperXTranscript, WhisperXWord
from openthot.models.transcript.wordcab import WordcabTranscript, WordcabWord


def wt2ott(wt: WhisperTranscript) -> OpenthotTranscript:
    ott = OpenthotTranscript(
        language=wt.language, text=wt.text, segments=[], speakers=set()
    )
    for wt_seg in wt.segments:
        otts = OpenthotSegment(
            id=wt_seg.id, start=wt_seg.start, end=wt_seg.end, words=[]
        )
        for wt_word in wt_seg.words:
            ottw = OpenthotWord(**wt_word.dict())
            otts.words.append(ottw)
        ott.segments.append(otts)
    return ott


def wtx2ott(wxt: WhisperXTranscript) -> OpenthotTranscript:
    ott = OpenthotTranscript(language=None, text="", segments=[], speakers=set())
    prev_word = WhisperXWord(
        word="", start=0.0, end=0.0, score=1.0, speaker=None
    ).dict()
    for i, wxt_seg in enumerate(wxt.segments):
        if wxt_seg.speaker:
            ott.speakers.add(wxt_seg.speaker)
        otts = OpenthotSegment(
            id=i,
            start=wxt_seg.start,
            end=wxt_seg.end,
            words=[],
            speaker=wxt_seg.speaker,
        )
        for wxt_word in wxt_seg.words:
            # fill none fields with previous word fields
            w_dict = prev_word | wxt_word.dict(exclude_none=True)
            ottw = OpenthotWord(**w_dict, probability=w_dict["score"])
            prev_word = w_dict
            otts.words.append(ottw)
        ott.segments.append(otts)
    return ott


def wc2ott(wc: WordcabTranscript) -> OpenthotTranscript:
    ott = OpenthotTranscript(
        language=wc.source_lang, text="", segments=[], speakers=set()
    )
    prev_word = WordcabWord(
        word="",
        start=0.0,
        end=0.0,
        score=1.0,
    ).dict()
    for i, wc_utt in enumerate(wc.utterances):
        if wc_utt.speaker is not None:
            ott.speakers.add(f"SPEAKER_{wc_utt.speaker}")
        otts = OpenthotSegment(
            id=i,
            start=wc_utt.start,
            end=wc_utt.end,
            words=[],
            speaker=f"SPEAKER_{wc_utt.speaker}" if wc_utt.speaker is not None else None,
        )
        for wc_word in wc_utt.words:
            # fill none fields with previous word fields
            w_dict = prev_word | wc_word.dict(exclude_none=True)
            ottw = OpenthotWord(**w_dict, probability=w_dict["score"])
            prev_word = w_dict
            otts.words.append(ottw)
        ott.segments.append(otts)
    return ott

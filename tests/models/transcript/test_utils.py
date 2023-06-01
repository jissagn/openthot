from pydantic import Json

from stt.models.transcript.sttsimple import SttSimpleTranscript
from stt.models.transcript.utils import wt2sttimple
from stt.models.transcript.whisper import WhisperTranscript


def test_wt2sttimple(whisper_output_example1: Json, stt_simple_example1: Json):
    wt = WhisperTranscript.parse_obj(whisper_output_example1)
    s: SttSimpleTranscript = wt2sttimple(wt)
    stt_simple_example1 = SttSimpleTranscript.parse_obj(stt_simple_example1)
    assert s == stt_simple_example1

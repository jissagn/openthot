from pydantic import Json

from stt.models.transcript.stt import SttTranscript
from stt.models.transcript.utils import wt2stt
from stt.models.transcript.whisper import WhisperTranscript


def test_wt2stt(whisper_output_example1: Json, stt_simple_example1: Json):
    wt = WhisperTranscript.parse_obj(whisper_output_example1)
    s: SttTranscript = wt2stt(wt)
    stt_simple_example1 = SttTranscript.parse_obj(stt_simple_example1)
    assert s == stt_simple_example1

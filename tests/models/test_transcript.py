from pydantic import Json

from stt.models.transcript import SttSimpleTranscript, WhisperTranscript, wt2sttimple


def test_transform_to_sttsimple(
    whisper_output_example1: Json, stt_simple_example1: Json
):
    wt = WhisperTranscript.parse_obj(whisper_output_example1)
    s: SttSimpleTranscript = wt2sttimple(wt)
    stt_simple_example1 = SttSimpleTranscript.parse_obj(stt_simple_example1)
    assert s == stt_simple_example1

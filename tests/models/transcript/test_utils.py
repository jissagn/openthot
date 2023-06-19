from stt.models.transcript.stt import SttTranscript
from stt.models.transcript.utils import wt2stt, wtx2stt
from stt.models.transcript.whisper import WhisperTranscript
from stt.models.transcript.whisperx import WhisperXTranscript


def test_wt2stt(
    whisper_output_example1: WhisperTranscript, stt_simple_example1: SttTranscript
):
    s: SttTranscript = wt2stt(whisper_output_example1)
    assert s == stt_simple_example1


def test_wtx2stt(
    whisperx_output_example2: WhisperXTranscript, stt_simple_example2: SttTranscript
):
    s: SttTranscript = wtx2stt(whisperx_output_example2)
    assert s == stt_simple_example2

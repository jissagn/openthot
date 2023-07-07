from openthot.models.transcript.openthot import OpenthotTranscript
from openthot.models.transcript.utils import wt2ott, wtx2ott
from openthot.models.transcript.whisper import WhisperTranscript
from openthot.models.transcript.whisperx import WhisperXTranscript


def test_wt2ott(
    whisper_output_example1: WhisperTranscript, ott_simple_example1: OpenthotTranscript
):
    s: OpenthotTranscript = wt2ott(whisper_output_example1)
    assert s == ott_simple_example1


def test_wtx2ott(
    whisperx_output_example2: WhisperXTranscript,
    ott_simple_example2: OpenthotTranscript,
):
    s: OpenthotTranscript = wtx2ott(whisperx_output_example2)
    assert s == ott_simple_example2

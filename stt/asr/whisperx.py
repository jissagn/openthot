import json
from pathlib import Path

import structlog
from stt.asr import Transcriptor
from stt.asr.utils import AsyncProcRunner

from stt.config import get_settings
from stt.models.transcript.whisperx import WhisperXTranscript

logger = structlog.get_logger(__file__)
model_size = get_settings().whisper_model_size
hf_token = get_settings().hf_token


class WhisperX(Transcriptor):
    async def run_transcription(
        self,
    ) -> None:
        proc_call = [
            "whisperx",
            self._audio_file_path,
            "--language",
            "fr",
            "--model",
            model_size,
            "--output_dir",
            Path(self._audio_file_path)
            .resolve()
            .parent,  # os.path.dirname(os.path.abspath(audio_file_path)),
            "--compute_type",
            "int8",
            "--diarize",
            "--hf_token",
            hf_token,
        ]

        proc_runner = AsyncProcRunner(proc_call)
        await proc_runner.run()
        self._transcript_duration = proc_runner.duration

        json_output_file = Path(self._audio_file_path).with_suffix(".json")

        with open(json_output_file, "r") as json_file:
            json_output = json.load(json_file)

        self._transcript = WhisperXTranscript.parse_obj(json_output)

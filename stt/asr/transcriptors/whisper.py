import json
from pathlib import Path

import structlog

from stt.asr.transcriptors import Transcriptor
from stt.asr.utils import AsyncProcRunner
from stt.config import get_settings
from stt.models.transcript.whisper import WhisperTranscript

logger = structlog.get_logger(__file__)
model_size = get_settings().whisper_model_size.value


class Whisper(Transcriptor):
    async def run_transcription(
        self,
    ) -> None:
        output_dir = str(
            Path(self._audio_file_path).resolve().parent
        )  # os.path.dirname(os.path.abspath(audio_file_path)),
        proc_call = [
            "whisper",
            self._audio_file_path,
            "--language",
            "fr",
            "--model",
            model_size,
            "--output_dir",
            output_dir,
            "--word_timestamps",
            "True",
        ]

        proc_runner = AsyncProcRunner(proc_call)
        await proc_runner.run()
        self._success = proc_runner.return_code == 0
        if not self.success:
            return

        self._transcript_duration = proc_runner.duration
        json_output_file = Path(self._audio_file_path).with_suffix(".json")
        with open(json_output_file, "r") as json_file:
            json_output = json.load(json_file)

        self._transcript = WhisperTranscript.parse_obj(json_output)

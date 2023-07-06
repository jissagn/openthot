import json
from pathlib import Path

import structlog

from stt.asr.transcriptors import Transcriptor
from stt.asr.utils import AsyncProcRunner
from stt.config import WhisperXSettings, get_settings
from stt.models.transcript.whisperx import WhisperXTranscript

logger = structlog.get_logger(__file__)
asr_settings = get_settings().asr


class WhisperX(Transcriptor):
    async def run_transcription(
        self,
    ) -> None:
        assert isinstance(asr_settings, WhisperXSettings)
        output_dir = str(
            Path(self._audio_file_path).resolve().parent
        )  # os.path.dirname(os.path.abspath(audio_file_path)),

        proc_call = [
            "whisperx",
            self._audio_file_path,
            "--language",
            "fr",
            "--model",
            asr_settings.model_size.value,
            "--output_dir",
            output_dir,
            "--compute_type",
            asr_settings.compute_type.value,
            "--diarize",
            "--hf_token",
            asr_settings.hf_token,
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

        self._transcript = WhisperXTranscript.parse_obj(json_output)

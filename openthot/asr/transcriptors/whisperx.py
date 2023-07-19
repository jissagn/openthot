import json
from pathlib import Path

import structlog

from openthot.asr.transcriptors import Transcriptor
from openthot.asr.utils import AsyncProcRunner, convert_file_to_wav, delete_file
from openthot.config import WhisperXSettings, get_settings
from openthot.models.transcript.whisperx import WhisperXTranscript

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

        if not str(self._audio_file_path).endswith(".wav"):
            wav_audio_file = await convert_file_to_wav(str(self._audio_file_path))
        else:
            wav_audio_file = str(self._audio_file_path.absolute())
        proc_call = [
            "whisperx",
            wav_audio_file,
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
        delete_file(wav_audio_file)
        self._success = proc_runner.return_code == 0
        if not self.success:
            await logger.aerror(
                "Async call did not go well",
                return_code=proc_runner.return_code,
                proc_call=proc_call,
                std_out=proc_runner.stdout,
                std_err=proc_runner.stderr,
            )
            return

        self._transcript_duration = proc_runner.duration
        json_output_file = Path(self._audio_file_path).with_suffix(".json")
        with open(json_output_file, "r") as json_file:
            json_output = json.load(json_file)

        self._transcript = WhisperXTranscript.parse_obj(json_output)

import httpx
import structlog

from stt.asr.transcriptors import Transcriptor
from stt.config import get_settings
from stt.models.transcript.wordcab import WordcabTranscript

logger = structlog.get_logger(__file__)
model_size = get_settings().whisper_model_size.value


class Wordcab(Transcriptor):
    async def run_transcription(
        self,
    ) -> None:
        with open(self._audio_file_path, "rb") as f:
            files = {"file": (self._audio_file_path, f.read())}
        async with httpx.AsyncClient(
            base_url="http://localhost:5001/api/v1"  # TODO: conf settings
        ) as client:
            r = await client.post(
                "/audio",
                files=files,  # type: ignore
                data={  # use `data` instead of `json` as the endpoint expects form data
                    "alignment": True,
                    "diarization": True,
                    "dual_channel": False,
                    "source_lang": "fr",
                    "timestamps": "s",
                    "use_batch": None,
                    "word_timestamps": True,
                },
                timeout=None,
            )
        self._success = r.status_code == 200
        if not self.success:
            await logger.aexception(
                "Coud not get transcription",
                http_return_json=r.json(),
                http_return_text=r.text,
            )
            return

        self._transcript_duration = r.elapsed.seconds
        json_output = r.json()
        self._transcript = WordcabTranscript.parse_obj(json_output)

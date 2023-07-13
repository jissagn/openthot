import httpx
import structlog

from openthot.asr.transcriptors import Transcriptor
from openthot.config import WordcabSettings, get_settings
from openthot.models.transcript.wordcab import WordcabTranscript

logger = structlog.get_logger(__file__)
asr_settings = get_settings().asr


class Wordcab(Transcriptor):
    async def run_transcription(
        self,
    ) -> None:
        assert isinstance(asr_settings, WordcabSettings)
        with open(self._audio_file_path, "rb") as f:
            files = {"file": (self._audio_file_path, f.read())}
        async with httpx.AsyncClient(base_url=asr_settings.url) as client:
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

        await logger.debug(
            "Transcription succeeded. Now gathering json output.",
        )
        self._transcript_duration = r.elapsed.seconds
        json_output = r.json()
        await logger.debug(
            "Parsing output json.",
        )
        self._transcript = WordcabTranscript.parse_obj(json_output)

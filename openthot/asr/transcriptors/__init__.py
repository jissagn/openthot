from abc import abstractclassmethod

from pydantic import FilePath

from openthot.models.transcript.whisper import WhisperTranscript
from openthot.models.transcript.whisperx import WhisperXTranscript
from openthot.models.transcript.wordcab import WordcabTranscript


class Transcriptor:
    _audio_file_path: FilePath
    _success: bool
    _transcript_duration: float
    _transcript: WhisperTranscript | WhisperXTranscript | WordcabTranscript

    def __init__(self, audio_file_path: FilePath) -> None:
        self._audio_file_path = audio_file_path

    @property
    def success(self):
        return self._success

    @property
    def transcript_duration(self) -> float:
        return self._transcript_duration

    @property
    def transcript(self):
        return self._transcript

    @abstractclassmethod
    async def run_transcription(
        self,
    ) -> None:
        pass

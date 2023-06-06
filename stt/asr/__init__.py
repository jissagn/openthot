from abc import abstractclassmethod

from pydantic import FilePath

from stt.models.transcript.whisper import WhisperTranscript
from stt.models.transcript.whisperx import WhisperXTranscript


class Transcriptor:
    _audio_file_path: FilePath
    _transcript_duration: float
    _transcript: WhisperTranscript | WhisperXTranscript

    def __init__(self, audio_file_path: FilePath) -> None:
        self._audio_file_path = audio_file_path

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

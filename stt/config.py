from enum import Enum
from functools import lru_cache
from typing import Literal

import structlog
from pydantic import AnyHttpUrl, BaseModel, BaseSettings, Extra, Field

from stt.models.transcript import TranscriptorSource

logger = structlog.get_logger(__file__)


class AsrComputeType(str, Enum):
    int8 = "int8"
    float16 = "float16"
    float32 = "float32"


class AsrModelSize(str, Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large-v2"


class Celery(BaseModel):
    """Settings that are specific to Celery"""

    task_always_eager: bool = False
    broker_url: str
    result_backend: str
    task_acks_late: bool = True


class WhisperSettings(BaseSettings):
    """Settings that are specific to Whisper"""

    engine: Literal[TranscriptorSource.whisper]
    model_size: AsrModelSize


class WhisperXSettings(BaseSettings):
    """Settings that are specific to WhisperX"""

    engine: Literal[TranscriptorSource.whisperx]
    model_size: AsrModelSize
    compute_type: AsrComputeType
    hf_token: str


class WordcabSettings(BaseSettings):
    """Settings that are specific to Wordcab"""

    engine: Literal[TranscriptorSource.wordcab]
    url: AnyHttpUrl


class Settings(BaseSettings):
    app_name: str = "OpenThot"
    asr: WhisperSettings | WhisperXSettings | WordcabSettings = Field(
        ..., discriminator="engine"
    )
    celery: Celery
    database_url: str
    users_token_root_secret: str
    object_storage_path: str

    class Config:
        env_file = ".env", ".env.prod", "secrets.env"
        env_nested_delimiter = "__"
        extra = Extra.forbid


@lru_cache()
def get_settings():
    return Settings()  # type: ignore

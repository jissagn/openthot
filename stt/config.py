from enum import Enum
from functools import lru_cache

from pydantic import AnyHttpUrl, BaseSettings

from stt.models.transcript import TranscriptorSource


class WhisperXComputeType(str, Enum):
    int8 = "int8"
    float16 = "float16"
    float32 = "float32"


class WhisperModelSize(str, Enum):
    tiny = "tiny"
    small = "small"
    medium = "medium"
    large = "large-v2"


class Settings(BaseSettings):
    app_name: str = "Sous-Titreur"
    asr_engine: TranscriptorSource
    celery_task_always_eager: bool = False
    celery_broker_url: str
    celery_result_backend: str
    celery_task_acks_late: bool = True
    database_url: str
    users_token_root_secret: str
    object_storage_path: str
    whisper_model_size: WhisperModelSize
    whisperx_compute_type: WhisperXComputeType
    wordcab_url: AnyHttpUrl
    hf_token: str

    class Config:
        env_file = ".env", ".env.prod", "secrets.env"


@lru_cache()
def get_settings():
    return Settings()  # type: ignore

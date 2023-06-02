from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Sous-Titreur"
    celery_broker_url: str
    celery_result_backend: str
    celery_task_acks_late: bool = True
    database_url: str
    users_token_root_secret: str
    object_storage_path: str
    whisper_model_size: str
    hf_token: str

    class Config:
        env_file = ".env", ".env.prod", "secrets.env"


@lru_cache()
def get_settings():
    return Settings()  # type: ignore

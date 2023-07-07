import os
import secrets
from pathlib import Path

import aiofiles
import structlog
from fastapi import UploadFile
from pydantic import FilePath

from openthot.config import get_settings

logger = structlog.get_logger(__file__)


async def save_audio_file(audio_file: UploadFile) -> FilePath:
    random_str = secrets.token_hex(16)
    filename = f"{random_str}-{audio_file.filename}"
    persistent_location: FilePath = Path(get_settings().object_storage_path, filename)

    await logger.adebug(
        "Intending to write audio file",
        persistent_location=persistent_location,
    )
    os.makedirs(os.path.dirname(os.path.abspath(persistent_location)), exist_ok=True)
    async with aiofiles.open(persistent_location, "wb") as persistent_file:
        await persistent_file.write(await audio_file.read())
    return persistent_location

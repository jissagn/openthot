import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

import structlog
from pydantic import FilePath

from stt.config import get_settings

logger = structlog.get_logger(__file__)
model_size = get_settings().whisper_model_size


def run_transcription(audio_file_path: FilePath) -> tuple[dict, str, float]:

    proc_call = [
        "whisper",
        audio_file_path,
        "--language",
        "fr",
        "--model",
        model_size,
        "--output_dir",
        os.path.dirname(os.path.abspath(audio_file_path)),
        "--word_timestamps",
        "True",
    ]
    logger.debug(
        "Calling whisper", proc_call=proc_call, audio_file_path=audio_file_path
    )
    start_time = datetime.now()
    result = subprocess.run(proc_call, capture_output=True)
    duration = (datetime.now() - start_time).total_seconds()
    logger.debug(
        f"Whisper done in {duration}s",
        proc_call=proc_call,
        audio_file_path=audio_file_path,
    )
    transcript = result.stdout.decode("utf-8")  # .split("\n")
    json_output_file = Path(audio_file_path).with_suffix(".json")

    with open(json_output_file, "r") as json_file:
        json_output = json.load(json_file)

    return json_output, transcript, duration

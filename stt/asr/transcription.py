import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from pydantic import FilePath

from stt.config import get_settings

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
    start_time = datetime.now()
    result = subprocess.run(proc_call, capture_output=True)
    duration = (datetime.now() - start_time).total_seconds()
    transcript = result.stdout.decode("utf-8")  # .split("\n")
    json_output_file = Path(audio_file_path).with_suffix(".json")

    with open(json_output_file, "r") as json_file:
        json_output = json.load(json_file)

    return json_output, transcript, duration

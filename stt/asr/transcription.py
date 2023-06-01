import asyncio
import json
from datetime import datetime
from pathlib import Path

import structlog
from pydantic import FilePath

from stt.config import get_settings
from stt.models.transcript.whisper import WhisperTranscript

logger = structlog.get_logger(__file__)
model_size = get_settings().whisper_model_size


async def run_transcription(
    audio_file_path: FilePath,
) -> tuple[WhisperTranscript, str, float]:
    audio_file_path = str(audio_file_path)  # type: ignore
    proc_call = [
        "whisper",
        audio_file_path,
        "--language",
        "fr",
        "--model",
        model_size,
        "--output_dir",
        Path(audio_file_path)
        .resolve()
        .parent,  # os.path.dirname(os.path.abspath(audio_file_path)),
        "--word_timestamps",
        "True",
    ]
    await logger.adebug(
        "Calling whisper",
        proc_call=" ".join([str(a) for a in proc_call]),
        audio_file_path=audio_file_path,
    )
    start_time = datetime.now()
    # result = subprocess.run(proc_call, capture_output=True, text=True)
    proc = await asyncio.create_subprocess_exec(
        *proc_call, stdout=asyncio.subprocess.PIPE
    )
    proc_out, proc_err = await proc.communicate()
    # await proc.wait()
    proc_out = str(proc_out, "utf8") if proc_out else ""
    proc_err = str(proc_err, "utf8") if proc_err else ""
    if proc.returncode != 0:
        logger.error(
            "Whisper failed",
            proc_call=" ".join([str(a) for a in proc_call]),
            audio_file_path=audio_file_path,
            output=proc_err.split("\n"),
        )
        raise Exception("Whisper failed")

    duration = (datetime.now() - start_time).total_seconds()
    logger.debug(
        f"Whisper done in {duration}s",
        proc_call=" ".join([str(a) for a in proc_call]),
        audio_file_path=audio_file_path,
    )
    transcript = proc_out
    json_output_file = Path(audio_file_path).with_suffix(".json")

    with open(json_output_file, "r") as json_file:
        json_output = json.load(json_file)

    wt = WhisperTranscript.parse_obj(json_output)

    return wt, transcript, duration

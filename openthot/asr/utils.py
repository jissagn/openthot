import asyncio
import time
from pathlib import Path

import structlog
from pydantic import FilePath

from openthot.exceptions import MissingASR

logger = structlog.get_logger(__file__)


class AsyncProcRunner:
    _proc_call: list[str]
    duration: float
    return_code: int | None
    stderr: str | None
    stdout: str | None

    def __init__(self, proc_call: list[str]) -> None:
        self._proc_call = [str(pc) for pc in proc_call]

    async def run(self):
        await logger.adebug(
            f"Calling `{self._proc_call[0]}`",
            proc_call=" ".join(self._proc_call),
        )
        start_time = time.perf_counter()
        try:
            proc = await asyncio.create_subprocess_exec(
                *self._proc_call, stdout=asyncio.subprocess.PIPE
            )
        except FileNotFoundError:
            raise MissingASR(asr_bin_name=self._proc_call[0])
        proc_out, proc_err = await proc.communicate()

        # Parse outputs
        self.stdout = str(proc_out, "utf8") if proc_out else None
        self.stderr = str(proc_err, "utf8") if proc_err else None
        self.duration = time.perf_counter() - start_time
        self.return_code = proc.returncode
        if proc.returncode != 0:
            logger.error(
                f"`{self._proc_call[0]}` failed",
                proc_call=" ".join(self._proc_call),
                stderr=proc_err,
            )
        await logger.adebug(
            f"`{self._proc_call[0]}` done in {self.duration}s",
            proc_call=" ".join(self._proc_call),
        )


async def convert_file_to_wav(filepath: str | Path | FilePath) -> Path:
    """
    Convert a file to wav format using ffmpeg.

    Args:
        filepath (str): Path to the file to convert.

    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If there is an error converting the file.

    Returns:
        str: Path to the converted file.
    """
    # Copyright 2023 The Wordcab Team. All rights reserved.
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File {filepath} does not exist.")

    new_filepath = filepath.with_suffix(".wav")
    cmd = [
        "ffmpeg",
        "-i",
        str(filepath.absolute()),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-y",
        str(new_filepath.absolute()),
    ]
    subproc = AsyncProcRunner(proc_call=cmd)
    await subproc.run()

    if subproc.return_code != 0:
        raise Exception(
            f"Error converting file {filepath} to wav format: {subproc.stdout}, {subproc.stderr}"
        )

    return new_filepath


def delete_file(filepath: str | Path | FilePath) -> None:
    """Delete a file.

    Args:
        filepath (str | Path | FilePath): Path to the file to delete.
    """
    if not isinstance(filepath, Path):
        filepath = Path(filepath)

    filepath.unlink(missing_ok=True)

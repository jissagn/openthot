import asyncio
import time

import structlog

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
        proc = await asyncio.create_subprocess_exec(
            *self._proc_call, stdout=asyncio.subprocess.PIPE
        )
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

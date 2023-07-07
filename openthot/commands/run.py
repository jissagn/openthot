import os
import subprocess
import sys
from enum import Enum
from typing import Optional

import typer

run = typer.Typer(help="Run a service.")


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"
    fatal = "fatal"


cwd = os.path.realpath(
    os.path.join(
        os.path.dirname(__file__), os.pardir, os.pardir
    )  # one way to get root dir of the project
)


@run.command()
def api(
    host: str = typer.Option("0.0.0.0", help="host of the api"),
    port: int = typer.Option(8000, help="port of the api"),
    reload: bool = typer.Option(False, help="watch the files and reload api on change"),
    gid: Optional[int] = typer.Option(
        None, help="Unix group to use when starting the worker"
    ),
    uid: Optional[int] = typer.Option(
        None, help="Unix user  to use when starting the worker"
    ),
):
    "Run api service."

    command = [
        "uvicorn",
        f"--host={host}",
        f"--port={port}",
        "openthot.api.main:app",
    ]

    if reload:
        command.append("--reload")

    if gid is not None:
        command.append(f"--gid={gid}")

    if uid is not None:
        command.append(f"--uid={uid}")

    sys.exit(
        subprocess.call(
            command,
            cwd=cwd,
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    )


@run.command()
def worker(
    concurrency: int = typer.Option(
        1,
        help=(
            "Number of child processes processing the queue."
            "The default is the number of CPUs available on your system."
        ),
    ),
    max_tasks_per_child: int = typer.Option(
        10000,
        help="Maximum number of tasks a pool worker can execute before it’s terminated and replaced by a new worker.",
    ),
    log_level: LogLevel = typer.Option(
        LogLevel.info, help="Logging level", case_sensitive=False
    ),
    gid: Optional[int] = typer.Option(
        None, help="Unix group to use when starting the worker"
    ),
    uid: Optional[int] = typer.Option(
        None, help="Unix user  to use when starting the worker"
    ),
):
    "Run background worker instance."

    command = [
        "celery",
        "--app=openthot.tasks.tasks.celery",
        "worker",
        f"--concurrency={concurrency}",
        f"--max-tasks-per-child={max_tasks_per_child}",
        f"--loglevel={log_level.value}",
    ]

    if gid is not None:
        command.append(f"--gid={gid}")

    if uid is not None:
        command.append(f"--uid={uid}")

    sys.exit(
        subprocess.call(
            command,
            cwd=cwd,
            env=os.environ,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
    )

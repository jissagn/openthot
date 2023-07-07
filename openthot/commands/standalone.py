import os
import sys
from subprocess import list2cmdline

import typer

cwd = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def standalone(workers: bool = typer.Option(True, help="Run asynchronous worker(s).")):
    "Starts both api and workers."
    from honcho.manager import Manager

    daemons = [("api", ["openthot", "run", "api"])]
    if workers:
        daemons.extend([("worker", ["openthot", "run", "worker"])])  # type: ignore

    manager = Manager()
    for name, cmd in daemons:
        manager.add_process(name, list2cmdline(cmd), quiet=False, cwd=cwd)

    manager.loop()
    sys.exit(manager.returncode)

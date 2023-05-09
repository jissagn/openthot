from functools import wraps
from typing import Any, Callable, Coroutine, ParamSpec, TypeVar

from asgiref import sync
from celery import Celery, Task

_P = ParamSpec("_P")
_R = TypeVar("_R")


def async_task(app: Celery, *args: Any, **kwargs: Any):
    """Decorator that allow to declare async functions as tasks,
    hence allowing usage of async interfaces for DB.
    Thanks to : https://stackoverflow.com/a/75437648
    Another interesting approach : https://stackoverflow.com/a/66318397"""

    def _decorator(func: Callable[_P, Coroutine[Any, Any, _R]]) -> Task:  # type: ignore
        sync_call = sync.AsyncToSync(func)

        @app.task(*args, **kwargs)
        @wraps(func)
        def _decorated(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            return sync_call(*args, **kwargs)

        return _decorated  # type: ignore

    return _decorator

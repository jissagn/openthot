from typing import Any, Sequence

from stt.exceptions import ExceptionModel, RichHTTPException


def error_responses_for_openapi(
    exceptions: Sequence[RichHTTPException] | None = None,
) -> dict[int | str, dict[str, Any]]:
    r = (
        {
            exc.status_code: {
                "model": ExceptionModel,
                "description": exc.description,
            }
            for exc in exceptions
        }
        if exceptions
        else {}
    )
    r[500] = {
        "model": ExceptionModel,
        "description": "Internal error",
    }
    return r  # type: ignore

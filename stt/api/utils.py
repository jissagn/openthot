from typing import Any, Sequence

from pydantic import BaseModel

from stt.exceptions import ExceptionModel, RichHTTPException


class ReturnedExceptionModel(BaseModel):
    """
    Class to wrap what we want to output, as
    FastAPI puts everything into a `detail` field.
    """

    detail: ExceptionModel


def error_responses_for_openapi(
    excs: Sequence[RichHTTPException] | None = None,
) -> dict[
    int | str, dict[str, Any]
]:  # "int | str" here is to make Pylance happy, but it really has int keys only
    """
        Helper to declare what JSON we return depending on errors status code.
        It's intended to be passed to the `responses` parameter of FastAPI routes.
        FastAPI will use this to generate proper OpenAPI documentation.

    Args:
        excs (Sequence[RichHTTPException] | None, optional): The exceptions that could be raised. Defaults to None.

    Returns:
        dict[int | str, dict[str, Any]]: The expected declaration of returned models.
    """
    r = (
        {
            exc.status_code: {
                "model": ReturnedExceptionModel,
                "description": exc.description,
            }
            for exc in excs
        }
        if excs
        else {}
    )
    r[500] = {
        "model": ReturnedExceptionModel,
        "description": "Internal error",
    }
    return r  # type: ignore

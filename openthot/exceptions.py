from typing import Dict

from fastapi import HTTPException
from pydantic import BaseModel


class ExceptionModel(BaseModel):
    description: str
    hint: str | None = None


class RichHTTPException(HTTPException):
    description: str

    def __init__(
        self,
        status_code: int,
        model: ExceptionModel,
        headers: Dict[str, str] | None = None,
    ) -> None:
        self.description = model.description
        super().__init__(status_code, model.dict(exclude_none=True), headers)


APIInterviewNotFound = RichHTTPException(
    status_code=404, model=ExceptionModel(description="Interview not found")
)
APIAudiofileMalformed = RichHTTPException(
    status_code=400,  # 422 is already "reserved"
    model=ExceptionModel(
        description="Could not load audio file",
        hint="Has it a valid extension (mp3, mp4, wav, ...) ?",
    ),
)


class BaseInternalError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MissingASR(BaseInternalError):
    def __init__(self, asr_bin_name: str) -> None:
        super().__init__(
            f"Could not launch subprocess. Is `{asr_bin_name}` installed ?"
        )

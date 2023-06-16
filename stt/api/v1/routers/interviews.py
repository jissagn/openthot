import os
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from stt.api.v1.routers import auth
from stt.db import rw
from stt.db.database import SqlaUserBase, get_db
from stt.exceptions import APIInternalError, APIInterviewNotFound
from stt.models.interview import (
    APIInputInterviewCreate,
    APIInputInterviewUpdate,
    APIOutputInterview,
    DBInputInterviewCreate,
    DBInputInterviewUpdate,
    TranscriptorSource,
)
from stt.object_storage import save_audio_file
from stt.tasks.tasks import process_audio_task

logger = structlog.get_logger(__file__)
router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)


@router.get(
    "/",
    response_model=list[APIOutputInterview] | None,
    response_model_exclude={"transcript"},
    response_model_exclude_none=True,
)
async def list_interviews(
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """List all existing interviews."""
    return list(await rw.get_interviews(db, current_user))


@router.post(
    "/",
    response_model=APIOutputInterview,
    responses={
        APIInternalError.status_code: {"description": APIInternalError.detail},
    },
)
async def create_interview(
    interview: APIInputInterviewCreate = Depends(),
    audio_file: UploadFile = File(description="The audio file of the interview."),
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Create a new interview to be transcripted."""
    audio_file_name: str = audio_file.filename or "interview"

    persistent_location = await save_audio_file(audio_file)
    await logger.adebug("Just wrote audio file.")
    interview_create = DBInputInterviewCreate(
        name=interview.name or str(Path(audio_file_name).with_suffix("")),
        audio_filename=audio_file_name,
        audio_location=persistent_location,
    )
    new_interview = await rw.create_interview(
        db,
        user=current_user,
        interview=interview_create,
    )
    try:
        process_audio_task.delay(
            user_id=current_user.id,
            interview_id=new_interview.id,
            audio_location=new_interview.audio_location,
            transcriptor_source=TranscriptorSource.whisper,
        )
    except Exception as e:
        logger.exception("Could not launch task")
        await rw.delete_interview(
            db, user=current_user, interview_id=jsonable_encoder(new_interview)["id"]
        )
        os.remove(persistent_location)
        raise APIInternalError from e
    return new_interview


@router.delete(
    "/{interview_id}",
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def delete_interview(
    interview_id: int,
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Delete a specific interview."""
    if not await rw.delete_interview(db, current_user, interview_id):
        raise APIInterviewNotFound


@router.get(
    "/{interview_id}",
    response_model=APIOutputInterview,
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def get_interview(
    interview_id: int,
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Get a specific interview."""
    interview = await rw.get_interview(db, current_user, interview_id)
    if interview:
        return interview
    raise APIInterviewNotFound


@router.get(
    "/{interview_id}/audio",
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def get_interview_audio(
    interview_id: int,
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Stream audio file of a given interview."""
    interview = await rw.get_interview(db, current_user, interview_id)
    if interview:
        headers = {"Cache-Control": "private, max-age=99999999, immutable"}
        if os.path.exists(interview.audio_location):
            await logger.adebug(
                "Streaming audio_file", audio_location=interview.audio_location
            )
            return FileResponse(interview.audio_location, headers=headers)
        elif interview.audio_location.startswith(("http",)):  # "s3:", "ftp:", ...
            raise NotImplementedError
        else:
            await logger.aerror(
                "Could not provide audio_file", audio_location=interview.audio_location
            )
            raise Exception
    raise APIInterviewNotFound


# @router.websocket("/{interview_id}/status")
# async def websocket_endpoint(websocket: WebSocket,
#     interview_id: int,
#     db=Depends(get_db),
#     current_user: DBUserBase = Depends(auth.current_active_user)):
#     await websocket.accept()
#     while True:
#         _ = await websocket.receive_json()
#         interview = await rw.get_interview(db, current_user, interview_id)
#         if interview:
#             await websocket.send_json(data={"status": interview.status})


@router.patch(
    "/{interview_id}",
    response_model=APIOutputInterview,
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def update_interview(
    interview_id: int,
    interview: APIInputInterviewUpdate,
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Update a specific interview."""
    interview_upd = DBInputInterviewUpdate(**interview.dict(exclude_unset=True))
    interview_db = await rw.get_interview(db, current_user, interview_id)
    if not interview_db:
        raise APIInterviewNotFound
    new_interview = await rw.update_interview(
        db, interview_db=interview_db, interview_upd=interview_upd
    )
    return new_interview

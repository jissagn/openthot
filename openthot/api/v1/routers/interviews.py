import os
from pathlib import Path

import librosa
import structlog
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from openthot.api.utils import error_responses_for_openapi
from openthot.api.v1.routers import auth
from openthot.asr.process import process_audio
from openthot.config import get_settings
from openthot.db import rw
from openthot.db.database import SqlaUserBase, get_db
from openthot.exceptions import APIAudiofileMalformed, APIInterviewNotFound
from openthot.models.interview import (
    APIInputInterviewCreate,
    APIInputInterviewUpdate,
    APIOutputInterview,
    DBInputInterviewCreate,
    DBInputInterviewUpdate,
    InterviewId,
)
from openthot.object_storage import save_audio_file
from openthot.tasks.tasks import process_audio_task

logger = structlog.get_logger(__file__)
router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)


@router.get(
    "/",
    response_model=list[APIOutputInterview] | None,
    responses=error_responses_for_openapi(),
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
    responses=error_responses_for_openapi((APIAudiofileMalformed,)),
    response_model_exclude_none=True,
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
    try:
        audio_duration = librosa.get_duration(path=persistent_location)
    except Exception as e:
        await logger.aexception(
            "Could not load audio file", persistent_location=persistent_location
        )
        os.remove(persistent_location)
        raise APIAudiofileMalformed from e
    interview_create = DBInputInterviewCreate(
        name=interview.name or str(Path(audio_file_name).with_suffix("")),
        audio_filename=audio_file_name,
        audio_location=persistent_location,
        audio_duration=audio_duration,
    )
    new_interview = await rw.create_interview(
        db,
        user=current_user,
        interview=interview_create,
    )
    try:
        if get_settings().celery.task_always_eager:
            await process_audio(
                session=db,
                user_id=current_user.id,
                interview_id=new_interview.id,
                audio_location=new_interview.audio_location,  # type: ignore
            )
        else:
            process_audio_task.delay(
                user_id=current_user.id,
                interview_id=new_interview.id,
                audio_location=new_interview.audio_location,
            )
    except Exception:
        await logger.aexception("Could not launch task of processing audio.")
        await rw.delete_interview(
            db, user=current_user, interview_id=jsonable_encoder(new_interview)["id"]
        )
        os.remove(persistent_location)
        raise
    return new_interview


@router.delete(
    "/{interview_id}",
    responses=error_responses_for_openapi((APIInterviewNotFound,)),
)
async def delete_interview(
    interview_id: InterviewId,
    db=Depends(get_db),
    current_user: SqlaUserBase = Depends(auth.current_active_user),
):
    """Delete a specific interview."""
    if not await rw.delete_interview(db, current_user, interview_id):
        raise APIInterviewNotFound


@router.get(
    "/{interview_id}",
    response_model=APIOutputInterview,
    responses=error_responses_for_openapi((APIInterviewNotFound,)),
)
async def get_interview(
    interview_id: InterviewId,
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
    responses=error_responses_for_openapi((APIInterviewNotFound,)),
)
async def get_interview_audio(
    interview_id: InterviewId,
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
#     interview_id: InterviewId,
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
    responses=error_responses_for_openapi((APIInterviewNotFound,)),
)
async def update_interview(
    interview_id: InterviewId,
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

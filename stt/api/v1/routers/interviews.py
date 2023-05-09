import os
import structlog
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.encoders import jsonable_encoder

from stt.api import auth
from stt.db import rw
from stt.db.database import DBUserBase, get_db
from stt.exceptions import APIInternalError, APIInterviewNotFound
from stt.models.interview import Interview, InterviewCreate, InterviewUpdate
from stt.object_storage import save_audio_file
from stt.tasks.tasks import process_audio_task

logger = structlog.get_logger(__file__)
router = APIRouter(
    prefix="/interviews",
    tags=["interviews"],
)


@router.get(
    "/",
    response_model=list[Interview] | None,
    response_model_exclude={"transcript"},
    response_model_exclude_none=True,
)
async def list_interviews(
    db=Depends(get_db), current_user: DBUserBase = Depends(auth.current_active_user)
):
    """List all existing interviews."""
    return list(await rw.get_interviews(db, current_user))


@router.post(
    "/",
    response_model=Interview,
    responses={
        APIInternalError.status_code: {"description": APIInternalError.detail},
    },
)
async def create_interview(
    interview: InterviewCreate = Depends(),
    audio_file: UploadFile = File(description="The audio file of the interview."),
    db=Depends(get_db),
    current_user: DBUserBase = Depends(auth.current_active_user),
):
    """Create a new interview to be transcripted."""
    persistent_location = await save_audio_file(audio_file)
    await logger.adebug("Just wrote audio file.")
    new_interview = await rw.create_interview(
        db, user=current_user, interview=interview, audio_location=persistent_location
    )
    try:
        process_audio_task.delay(
            user_id=current_user.id,
            interview_id=new_interview.id,
            audio_location=new_interview.audio_location,
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
    current_user: DBUserBase = Depends(auth.current_active_user),
):
    """Delete a specific interview."""
    if not await rw.delete_interview(db, current_user, interview_id):
        raise APIInterviewNotFound


@router.get(
    "/{interview_id}",
    response_model=Interview,
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def get_interview(
    interview_id: int,
    db=Depends(get_db),
    current_user: DBUserBase = Depends(auth.current_active_user),
):
    """Get a specific interview."""
    interview = await rw.get_interview(db, current_user, interview_id)
    if interview:
        return interview
    raise APIInterviewNotFound


@router.patch(
    "/{interview_id}",
    response_model=Interview,
    responses={
        APIInterviewNotFound.status_code: {"description": APIInterviewNotFound.detail},
    },
)
async def update_interview(
    interview_id: int,
    interview: InterviewUpdate,
    db=Depends(get_db),
    current_user: DBUserBase = Depends(auth.current_active_user),
):
    """Update a specific interview."""
    interview_target = await rw.get_interview(db, current_user, interview_id)
    if not interview_target:
        raise APIInterviewNotFound
    new_interview = await rw.update_interview(
        db, interview_db=interview_target, interview_upd=interview
    )
    return new_interview

import os
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from stt.config import get_settings

from stt.db import rw
from stt.db.database import create_db_and_tables, get_db
from stt.models.interview import Interview, InterviewCreate, InterviewUpdate
from stt.tasks.tasks import process_audio_task

app = FastAPI()


@app.on_event("startup")
async def startup():
    await create_db_and_tables()


@app.get("/status")
async def get_status():
    return {"status": "OK"}


@app.get(
    "/interviews/",
    response_model=list[Interview] | None,
    response_model_exclude={"transcript"},
    response_model_exclude_none=True,
)
async def list_interviews(db=Depends(get_db)):
    """List all existing interviews."""
    return list(rw.get_interviews(db))


@app.post("/interviews/", response_model=Interview)
async def new_interview(
    interview: InterviewCreate = Depends(),
    audio_file: UploadFile = File(description="The audio file of the interview."),
    db=Depends(get_db),
):
    """Create a new interview to be transcripted."""
    persistent_location = Path(get_settings().object_storage_path, audio_file.filename)
    os.makedirs(os.path.dirname(os.path.abspath(persistent_location)), exist_ok=True)
    with open(persistent_location, "wb") as persistent_file:
        persistent_file.write(audio_file.file.read())
    print(f"Just wrote {persistent_location}")
    interview = rw.create_interview(
        db, interview=interview, audio_location=persistent_location
    )
    process_audio_task.delay(
        interview_id=interview.id, audio_location=interview.audio_location
    )
    return interview


@app.get("/interviews/{interview_id}", response_model=Interview)
async def get_interview(interview_id: int, db=Depends(get_db)):
    """Get a specific interview."""
    interview = rw.get_interview(db, interview_id)
    if interview:
        return interview
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Interview does not exist."
    )


@app.patch("/interviews/{interview_id}", response_model=Interview)
async def update_interview(
    interview_id: int, interview: InterviewUpdate, db=Depends(get_db)
):
    """Update a specific interview."""
    interview_target = rw.get_interview(db, interview_id)
    if not interview_target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interview does not exist."
        )
    interview = rw.update_interview(
        db, interview_db=interview_target, interview_upd=interview
    )
    return interview

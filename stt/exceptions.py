from fastapi import HTTPException

# class TaskLaunchException(Exception):
#     pass


APIInterviewNotFound = HTTPException(status_code=404, detail="Interview not found")
APIAudiofileMalformed = HTTPException(
    status_code=422,
    detail="Could not load audio file. Has it a valid extension (mp3, mp4, wav, ...) ?",
)
APIInternalError = HTTPException(
    status_code=500, detail="Could not process request. Please try again later."
)

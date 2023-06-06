from fastapi import HTTPException

# class TaskLaunchException(Exception):
#     pass


APIInterviewNotFound = HTTPException(status_code=404, detail="Interview not found")
APIInternalError = HTTPException(
    status_code=500, detail="Could not process request. Please try again later."
)

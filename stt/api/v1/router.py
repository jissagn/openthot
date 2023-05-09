import structlog
from fastapi import APIRouter, Depends

from stt.api import auth
from stt.api.v1.routers import interviews
from stt.db.database import DBUserBase


logger = structlog.get_logger(__file__)
v_router = APIRouter()


@v_router.get("/authenticated-route", tags=["example"])
async def authenticated_route(user: DBUserBase = Depends(auth.current_active_user)):
    return {"message": f"Hello {user.email}!"}


v_router.include_router(interviews.router)

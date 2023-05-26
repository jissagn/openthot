import structlog
from fastapi import APIRouter

from stt.api.v1.routers import interviews, auth, users


logger = structlog.get_logger(__file__)
v_router = APIRouter()

v_router.include_router(interviews.router)
v_router.include_router(auth.router)
v_router.include_router(users.router)

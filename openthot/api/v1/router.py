import structlog
from fastapi import APIRouter

from openthot.api.v1.routers import auth, interviews, users

logger = structlog.get_logger(__file__)
v_router = APIRouter()

v_router.include_router(interviews.router)
v_router.include_router(auth.router)
v_router.include_router(users.router)

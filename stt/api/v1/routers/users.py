import structlog
from fastapi import APIRouter

from stt.api.v1.routers import auth
from stt.models.users import UserRead, UserUpdate

logger = structlog.get_logger(__file__)
router = APIRouter(prefix="/users", tags=["users"])


router.include_router(
    auth.fastapi_users_subapp.get_users_router(UserRead, UserUpdate),
)

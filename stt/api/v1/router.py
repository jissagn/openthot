import structlog
from fastapi import APIRouter, Depends

from stt.api.v1 import auth
from stt.api.v1.routers import interviews
from stt.db.database import DBUserBase
from stt.models.users import UserCreate, UserRead, UserUpdate

logger = structlog.get_logger(__file__)
v_router = APIRouter()


@v_router.get("/authenticated-route", tags=["example"])
async def authenticated_route(user: DBUserBase = Depends(auth.current_active_user)):
    return {"message": f"Hello {user.email}!"}


v_router.include_router(interviews.router)


#
# Auth
#
v_router.include_router(
    auth.fastapi_users_subapp.get_auth_router(auth.auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
v_router.include_router(
    auth.fastapi_users_subapp.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
v_router.include_router(
    auth.fastapi_users_subapp.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
v_router.include_router(
    auth.fastapi_users_subapp.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


#
# Users
#
v_router.include_router(
    auth.fastapi_users_subapp.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

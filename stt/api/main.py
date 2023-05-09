import structlog
from fastapi import FastAPI
from stt.api import auth

from stt.api.v1.router import v_router as v1_router
from stt.db.database import close_clean_up_pooled_connections, create_db_and_tables
from stt.models.users import UserCreate, UserRead, UserUpdate

logger = structlog.get_logger(__file__)
app = FastAPI()


@app.get("/status")
async def get_status():
    return {"status": "OK"}


#
# Special events
#
@app.on_event("startup")
async def startup():
    # Not needed if Alembic
    await logger.ainfo("Starting up...")
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown():
    await logger.ainfo("Shutting down...")
    await close_clean_up_pooled_connections()


#
# API
#
app.include_router(v1_router, prefix="/api/v1")


#
# Auth
#
app.include_router(
    auth.fastapi_users_subapp.get_auth_router(auth.auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    auth.fastapi_users_subapp.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    auth.fastapi_users_subapp.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    auth.fastapi_users_subapp.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)


#
# Users
#
app.include_router(
    auth.fastapi_users_subapp.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

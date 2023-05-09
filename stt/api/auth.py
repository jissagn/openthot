import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from stt.config import get_settings
from stt.db.database import DBUserBase, get_user_db


class UserManager(UUIDIDMixin, BaseUserManager[DBUserBase, uuid.UUID]):  # type: ignore
    reset_password_token_secret = get_settings().users_token_root_secret
    verification_token_secret = get_settings().users_token_root_secret

    async def on_after_register(
        self, user: DBUserBase, request: Optional[Request] = None
    ):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: DBUserBase, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: DBUserBase, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=get_settings().users_token_root_secret, lifetime_seconds=3600
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users_subapp = FastAPIUsers[DBUserBase, uuid.UUID](get_user_manager, [auth_backend])  # type: ignore

current_active_user = fastapi_users_subapp.current_user(active=True)

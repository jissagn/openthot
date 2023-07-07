import uuid

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate

UserId = uuid.UUID


class UserRead(BaseUser[UserId]):
    pass


class UserCreate(BaseUserCreate):
    pass


class UserUpdate(BaseUserUpdate):
    pass

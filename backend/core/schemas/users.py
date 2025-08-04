from pydantic import BaseModel

from core.schemas.common import IdSchema


class UserSchema(BaseModel):
    username: str


class UserForTemplateSchema(IdSchema, UserSchema):
    pass


class UserInSchema(UserSchema):
    password: str


class UserCreateSchema(UserInSchema):
    telegram_id: int


class UserTelegramIdSchema(BaseModel):
    telegram_id: int


class CredentialsSchema(UserCreateSchema):
    password: bytes


class TokenSchema(BaseModel):
    access_token: str


class UserActivitySchema(BaseModel):
    is_active: bool

from pydantic import BaseModel

from core.enums import Languages


class UserTelegramIdSchema(BaseModel):
    telegram_id: int


class UserSchema(UserTelegramIdSchema):
    access_token: str


class UserUpdateSchema(BaseModel):
    access_token: str | None = None
    language: Languages | None = None

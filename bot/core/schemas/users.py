from pydantic import BaseModel


class UserTelegramIdSchema(BaseModel):
    telegram_id: int


class UserSchema(UserTelegramIdSchema):
    access_token: str


class UserUpdateSchema(BaseModel):
    access_token: str | None = None
    language: str | None = None

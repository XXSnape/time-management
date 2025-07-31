from pydantic import BaseModel


class UserSchema(BaseModel):
    telegram_id: int
    access_token: str

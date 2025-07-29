from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str


class UserInSchema(UserSchema):
    password: str


class UserCreateSchema(UserInSchema):
    telegram_id: int


class CredentialsSchema(UserCreateSchema):
    password: bytes


class TokenSchema(BaseModel):
    access_token: str

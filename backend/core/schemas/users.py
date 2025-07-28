from pydantic import BaseModel


class UserSchema(BaseModel):
    username: str


class UserInSchema(UserSchema):
    password: str


class CredentialsSchema(UserInSchema):
    password: bytes


class TokenSchema(BaseModel):
    access_token: str

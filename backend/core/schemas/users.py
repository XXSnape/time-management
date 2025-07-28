from pydantic import BaseModel


class SignUpSchema(BaseModel):
    username: str
    password: str


class CredentialsSchema(SignUpSchema):
    password: bytes


class TokenSchema(BaseModel):
    access_token: str

from pydantic import BaseModel


class ResultSchema(BaseModel):
    result: bool

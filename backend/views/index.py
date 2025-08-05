from fastapi import APIRouter, Request
from fastapi.params import Header
from typing import Annotated
from core.dependencies.auth import UserDep
from core.utils.templates import templates


router = APIRouter()


@router.get("/")
async def index(
    request: Request,
    user: UserDep,
    accept_language: Annotated[str, Header()],
):
    # get_locale
    print(accept_language)
    return templates.TemplateResponse(
        "index.html", {"request": request, "username": user.username}
    )

from core.dependencies.auth import UserDep
from core.dependencies.language import Translations
from core.utils.templates import templates
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def index(
    request: Request,
    user: UserDep,
    translations: Translations,
):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": user.username,
            **translations,
        },
    )

from fastapi import APIRouter, Request
from core.dependencies.auth import UserDep
from core.utils.templates import templates


router = APIRouter()


@router.get("/")
async def index(
    request: Request,
    user: UserDep,
):
    return templates.TemplateResponse(
        "index.html", {"request": request, "username": user.username}
    )

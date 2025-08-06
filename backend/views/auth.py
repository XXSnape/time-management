from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from typing_extensions import Annotated

from core.config import settings
from core.dependencies.db import SessionWithoutCommit
from core.dependencies.language import Translations
from core.schemas.users import UserInSchema
from core.utils.templates import templates
from services.users import create_new_access_token

router = APIRouter()


@router.get("/login")
async def login_page(request: Request, translations: Translations):
    return templates.TemplateResponse(
        "login.html", {"request": request, **translations}
    )


@router.post("/login")
async def login(
    user_in: Annotated[UserInSchema, Form()],
    session: SessionWithoutCommit,
):
    try:
        token = await create_new_access_token(
            user_in=user_in, session=session
        )
    except HTTPException:
        return RedirectResponse(
            url="login?error=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    response = RedirectResponse(
        url="/", status_code=status.HTTP_303_SEE_OTHER
    )
    response.set_cookie(
        key=settings.auth_jwt.cookie_key_token,
        value=token.access_token,
        httponly=True,
    )
    return response

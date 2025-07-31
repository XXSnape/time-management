from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram.utils.i18n import gettext as _
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from httpx import AsyncClient, codes

from core.config import settings
from core.enums import Methods
from core.utils.request import make_request
from .states import AuthState


async def enter_login_to_register(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.switch_to(AuthState.register_username)


def is_short_login(text: str):
    if len(text) <= 40:
        return text
    raise ValueError


async def incorrect_login(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.answer(
        _("Логин должен быть не длиннее 40 символов")
    )


async def correct_login(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    text: str,
) -> None:
    client: AsyncClient = dialog_manager.middleware_data["client"]
    json = await make_request(
        client=client, endpoint=f"users/{text}", method=Methods.get
    )
    if json["result"]:
        await message.delete()
        await message.answer(
            _(
                "Пользователь «{username}» уже существует, регистрация не нужна"
            ).format(username=text)
        )
        await dialog_manager.switch_to(
            AuthState.login_or_registration
        )
        return

    dialog_manager.dialog_data.update(username=text)
    await dialog_manager.switch_to(AuthState.password)

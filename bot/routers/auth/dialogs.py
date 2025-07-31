from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from routers.auth.states import AuthState
from . import getters


async def click_process(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await callback.message.edit_text(text="Hello!")
    await dialog_manager.done()


auth_dialog = Dialog(
    Window(
        Format(text="{request_text}"),
        Button(
            text=Format("{enter_text}"),
            id="enter",
            on_click=click_process,
        ),
        Button(
            text=Format("{register_text}"),
            id="register",
            on_click=click_process,
        ),
        getter=getters.login_or_register,
        state=AuthState.login_or_registration,
    ),
)

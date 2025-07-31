from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from routers.auth.states import AuthState
from . import getters
from . import handlers


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
            on_click=handlers.enter_login_to_register,
        ),
        getter=getters.login_or_register,
        state=AuthState.login_or_registration,
    ),
    Window(
        Format(text="{text}"),
        TextInput(
            id="username_input",
            type_factory=handlers.is_short_login,
            on_success=handlers.correct_login,
            on_error=handlers.incorrect_login,
        ),
        getter=getters.enter_username,
        state=AuthState.register_username,
    ),
    Window(
        Format(text="{text}"),
        # TextInput(
        #     id="password_input",
        #     type_factory=handlers.is_short_login,
        #     on_success=handlers.correct_login,
        #     on_error=handlers.incorrect_login,
        # ),
        getter=getters.enter_password,
        state=AuthState.password,
    ),
)

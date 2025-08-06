from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Format

from core.config import settings
from routers.auth.states import AuthState
from routers.common.handlers import is_short_text, on_incorrect_text

from . import getters, handlers


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
        SwitchTo(
            text=Format("{register_text}"),
            id="register",
            state=AuthState.register_username,
            when="is_not_logged_in",
        ),
        SwitchTo(
            text=Format("{update_session_text}"),
            id="update_session",
            state=AuthState.login_username,
            when="is_logged_in",
        ),
        getter=getters.auth,
        state=AuthState.login_or_registration,
    ),
    Window(
        Format(text="{text}"),
        TextInput(
            id="register_username_input",
            type_factory=is_short_text(
                max_length=settings.bot.max_login_length,
            ),
            on_success=handlers.correct_login,
            on_error=on_incorrect_text,
        ),
        getter=getters.enter_username,
        state=AuthState.register_username,
    ),
    Window(
        Format(text="{text}"),
        TextInput(
            id="login_username_input",
            on_success=handlers.unverified_login,
        ),
        getter=getters.enter_username,
        state=AuthState.login_username,
    ),
    Window(
        Format(text="{text}"),
        SwitchTo(
            text=Format("{back}"),
            id="back_to_register_username",
            state=AuthState.register_username,
        ),
        TextInput(
            id="register_password_input",
            on_success=handlers.create_user,
        ),
        getter=getters.enter_password,
        state=AuthState.register_password,
    ),
    Window(
        Format(text="{text}"),
        SwitchTo(
            text=Format("{back}"),
            id="back_to_login_username",
            state=AuthState.login_username,
        ),
        TextInput(
            id="login_password_input",
            on_success=handlers.login_user,
        ),
        getter=getters.enter_password,
        state=AuthState.login_password,
    ),
)

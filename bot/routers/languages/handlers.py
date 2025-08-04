from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, ManagedRadio

from core.enums import Languages
from core.schemas.users import UserTelegramIdSchema, UserUpdateSchema
from database.dao.users import UsersDAO


async def set_default_language(
    start_data: Any, manager: DialogManager
):
    session = manager.middleware_data["session_without_commit"]
    lang = await UsersDAO(
        session=session
    ).get_user_locale_by_telegram_id(manager.event.from_user.id)
    radio: ManagedRadio = manager.find("r_languages")
    await radio.set_checked(lang)


async def change_language(
    callback: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    session = dialog_manager.middleware_data["session_with_commit"]
    radio: ManagedRadio = dialog_manager.find("r_languages")
    lang: Languages = radio.get_checked()
    await UsersDAO(session=session).update(
        filters=UserTelegramIdSchema(
            telegram_id=callback.from_user.id
        ),
        values=UserUpdateSchema(language=lang),
    )
    if lang == Languages.ru:
        success = "✅Язык успешно обновлен!"
    else:
        success = "✅The language has been successfully updated!"
    await dialog_manager.done()
    await callback.answer(success, show_alert=True)

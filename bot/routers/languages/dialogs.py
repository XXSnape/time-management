import operator

from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Radio
from aiogram_dialog.widgets.text import Format

from . import getters, handlers
from .states import LanguagesStates

change_language_dialog = Dialog(
    Window(
        Format(text="{text}"),
        Radio(
            Format("🔘 {item[0]}"),
            Format("⚪️ {item[0]}"),
            id="r_languages",
            item_id_getter=operator.itemgetter(1),
            items="languages",
        ),
        Button(
            text=Format(text="{save}"),
            id="save_lang",
            on_click=handlers.change_language,
        ),
        state=LanguagesStates.change,
        getter=getters.choose_language,
    ),
    on_start=handlers.set_default_language,
)

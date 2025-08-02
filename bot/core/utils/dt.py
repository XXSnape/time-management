import datetime
from zoneinfo import ZoneInfo

from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _


def get_moscow_dt() -> datetime.datetime:
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    return moscow_dt


def convert_utc_to_moscow(
    utc_dt: datetime.datetime,
) -> datetime.datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
    return utc_dt.astimezone(ZoneInfo("Europe/Moscow"))


def convert_moscow_dt_to_utc(
    moscow_dt: datetime.datetime,
) -> datetime.datetime:
    moscow_tz = ZoneInfo("Europe/Moscow")
    moscow_dt_aware = moscow_dt.replace(tzinfo=moscow_tz)
    return moscow_dt_aware.astimezone(datetime.timezone.utc)


def parse_utc_string_to_dt(dt_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        dt_str,
        "%Y-%m-%dT%H:%M:%SZ",
    )


def get_pretty_dt(dt_str: str) -> str:
    dt = parse_utc_string_to_dt(dt_str)
    moscow_dt = convert_utc_to_moscow(dt)
    return moscow_dt.strftime("%d.%m.%Y %H:%M")


async def selected_date_validator(
    callback: CallbackQuery,
    selected_date: datetime.date,
) -> bool:
    dt = get_moscow_dt()
    if (
        selected_date < dt.date()
        or selected_date == dt.date()
        and dt.hour == 23
    ):
        await callback.answer(
            _(
                "Дата должна быть позже или равна сегодняшней по Москве"
            )
        )
        return False
    return True

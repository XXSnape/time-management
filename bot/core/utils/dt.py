import datetime
from zoneinfo import ZoneInfo


def get_moscow_tz_and_dt() -> (
    tuple[datetime.timezone, datetime.datetime]
):
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    return moscow_tz, moscow_dt


def convert_utc_to_moscow(
    utc_dt: datetime.datetime,
) -> datetime.datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
    return utc_dt.astimezone(ZoneInfo("Europe/Moscow"))


def get_pretty_dt(dt_str: str) -> str:
    dt = datetime.datetime.strptime(
        dt_str,
        "%Y-%m-%dT%H:%M:%SZ",
    )
    moscow_dt = convert_utc_to_moscow(dt)
    return moscow_dt.strftime("%d.%m.%Y %H:%M")

import datetime
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status


def validate_dt(
    deadline_datetime: datetime.datetime,
) -> datetime.datetime:
    now = datetime.datetime.now(datetime.UTC)
    if deadline_datetime.tzinfo is None:
        deadline_utc = deadline_datetime.replace(tzinfo=datetime.UTC)
    else:
        deadline_utc = deadline_datetime.astimezone(datetime.UTC)
    if now >= deadline_utc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Входящие дата и время меньше, чем текущее",
        )
    return deadline_utc


def parse_utc_string_to_dt(dt_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(
        dt_str,
        "%Y-%m-%dT%H:%M:%SZ",
    )


def convert_utc_to_moscow(
    utc_dt: datetime.datetime,
) -> datetime.datetime:
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
    return utc_dt.astimezone(ZoneInfo("Europe/Moscow"))

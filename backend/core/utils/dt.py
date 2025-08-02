import datetime

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

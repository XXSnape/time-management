import datetime


def get_moscow_tz_and_dt() -> (
    tuple[datetime.timezone, datetime.datetime]
):
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    return moscow_tz, moscow_dt


def get_pretty_dt(dt_str: str) -> str:
    dt = datetime.datetime.strptime(
        dt_str,
        "%Y-%m-%dT%H:%M:%SZ",
    )
    return dt.strftime("%d.%m.%Y %H:%M")

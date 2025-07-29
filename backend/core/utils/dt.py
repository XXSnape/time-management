import datetime


def get_moscow_tz_and_dt() -> tuple[datetime.timezone, datetime.datetime]:
    moscow_tz = datetime.timezone(datetime.timedelta(hours=3))
    moscow_dt = datetime.datetime.now(moscow_tz)
    return moscow_tz, moscow_dt

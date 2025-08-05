from core.utils.enums import Weekday


def localize_periods(language: str, result: dict):
    if language == "ru":
        for stat, period in zip(
            result["items"],
            [
                "1 Неделя",
                "1 Месяц",
                "3 Месяца",
                "6 Месяцев",
                "9 Месяцев",
                "1 Год",
                "Все время",
            ],
        ):
            stat["period"] = period


def localize_weekdays(language: str):
    if language == "ru":
        days = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
    else:
        days = [day.title() for day in Weekday]
    return [(day, value) for day, value in zip(days, Weekday)]

from enum import StrEnum, auto
from typing import Literal


class Weekday(StrEnum):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()


Periods = Literal[
    "1 Week",
    "1 Month",
    "3 Months",
    "6 Months",
    "9 Months",
    "1 Year",
    "Аll time",
]

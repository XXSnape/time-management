from enum import StrEnum

from enum import StrEnum, auto


class Weekday(StrEnum):
    monday = auto()
    tuesday = auto()
    wednesday = auto()
    thursday = auto()
    friday = auto()
    saturday = auto()
    sunday = auto()


class Languages(StrEnum):
    ru = "ru"
    en = "en"


class Methods(StrEnum):
    get = "get"
    post = "post"
    delete = "delete"
    patch = "patch"

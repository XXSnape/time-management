from enum import StrEnum


class Languages(StrEnum):
    ru = "ru"
    en = "en"


class Methods(StrEnum):
    get = "get"
    post = "post"
    delete = "delete"
    patch = "patch"

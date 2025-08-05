from typing import Annotated, TypeAlias

from fastapi import Header, Depends, Request


def get_locale(
    accept_language: Annotated[
        str | None,
        Header(),
    ] = None,
):
    if accept_language is None:
        return "ru"
    if "ru" in accept_language:
        return "ru"
    if "en" in accept_language:
        return "en"
    return "ru"


def get_translations(
    language: Annotated[str, Depends(get_locale)], request: Request
):
    return request.app.state.translations[language]


Language: TypeAlias = Annotated[str, Depends(get_locale)]
Translations: TypeAlias = Annotated[
    dict[str, str], Depends(get_translations)
]

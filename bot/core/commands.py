from enum import StrEnum


class Commands(StrEnum):
    start = "Знакомство с ботом"
    auth = "Авторизация"
    create = "Создать новую задачу / привычку"
    view = "Посмотреть задачи / привычки"
    stats = "Статистика по задачам / привычкам"
    cancel = "Отменить (перезапустить)"

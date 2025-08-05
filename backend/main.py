import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from api import router as api_router
from core.config import settings
from core.dependencies.db import db_helper
from core.utils.exc import RedirectException
from views import router as views_router

logging.basicConfig(
    level=settings.logging.log_level_value,
    format=settings.logging.log_format,
)


def f():
    return {
        "ru": {
            "app_text": "Задачи и привычки",
            "login_text": "Логин",
            "invalid_login_text": "Неверный логин или пароль",
            "username_text": "Никнейм",
            "password_text": "Пароль",
            "to_main_text": "На главную",
            "my_tasks": "Мои задачи",
            "stats_text": "📊 Статистика",
            "create_text": "+ Создать",
            "no_tasks_text": "Нет задач",
            "deadline_text": "Дата дедлайна по Москве",
            "edit_text": "✏️Редактировать",
            "delete_text": "🗑️Удалить",
            "back_text": "Назад",
            "forward_text": "Вперед →",
            "create_task_text": "+ Создать новую задачу",
            "task_name": "Название задачи",
            "max_40_text": "Максимум 40 символов",
            "description_text": "Описание",
            "max_250": "Максимум 250 символов",
            "reminder_text": "Напомнить за (часов)",
            "reminder_constraint_text": "От 1 до 24 часов",
            "cancel_text": "Отмена",
            "edit_task_text": "✏️Редактировать задачу",
            "save_changes_text": "Сохранить изменения",
            "completed_text": "✓ Выполнена",
            "mark_text": "Отметить завершённой",
            "tasks_stats_text": "📊Статистика выполнения задач",
            "all_tasks_text": "Всего задач:",
            "all_completed_text": "Выполнено:",
            "not_completed_text": "Не выполнено:",
            "performance_text": "Процент выполнения:",
            "my_habits_text": "Мои привычки",
            "no_habits_text": "Нет привычек",
            "create_habit_text": "Создать привычку",
            "habit_name_text": "Название привычки",
            "habit_purpose_text": "Цель привычки",
            "days_text": "Дни недели",
            "habit_reminder_text": "Часы напоминания (0-23)",
            "create_new_habit_text": "Создать новую привычку",
            "edit_habit_text": "✏️Редактировать привычку",
            "habits_stats_text": "📊Статистика выполнения привычек",
            "habit_completed_text": "Всего завершено привычек",
        },
        "en": {
            "app_text": "Tasks and Habits",
            "login_text": "Login",
            "invalid_login_text": "Invalid login or password",
            "username_text": "Nickname",
            "password_text": "Password",
            "to_main_text": "To the main page",
            "my_tasks": "My tasks",
            "stats_text": "📊 Statistics",
            "create_text": "+ Create",
            "no_tasks_text": "No tasks",
            "deadline_text": "Deadline date in Moscow",
            "edit_text": "✏️Edit",
            "delete_text": "🗑️Delete",
            "back_text": "Back",
            "forward_text": "Forward →",
            "create_task_text": "+ Create a new task",
            "task_name": "Task name",
            "max_40_text": "Maximum 40 characters",
            "description_text": "Description",
            "max_250": "Maximum 250 characters",
            "reminder_text": "Remind me in (hours)",
            "reminder_constraint_text": "1 to 24 hours",
            "cancel_text": "Cancel",
            "edit_task_text": "✏️Edit task",
            "save_changes_text": "Save changes",
            "completed_text": "✓ Completed",
            "mark_text": "Mark Completed",
            "tasks_stats_text": "📊Task performance statistics",
            "all_tasks_text": "Total tasks:",
            "all_completed_text": "Completed:",
            "not_completed_text": "Not completed:",
            "performance_text": "Percentage of completion:",
            "my_habits_text": "My habits",
            "no_habits_text": "No habits",
            "create_habit_text": "Create a habit",
            "habit_name_text": "Name of the habit",
            "habit_purpose_text": "Purpose of the habit",
            "days_text": "Days of the week",
            "habit_reminder_text": "Reminder hours (0-23)",
            "create_new_habit_text": "Create a new habit",
            "edit_habit_text": "✏️Edit habit",
            "habits_stats_text": "📊 Habits completion statistics",
            "habit_completed_text": "Habits completed",
        },
    }


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Завершает соединение с базой данных.
    """
    app.state.translations = f()

    yield
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
)
main_app.include_router(api_router)
main_app.include_router(views_router)
main_app.mount(
    "/static", StaticFiles(directory="static"), name="static"
)


@main_app.exception_handler(RedirectException)
async def redirect_exception_handler(
    request: Request, exc: RedirectException
):
    return RedirectResponse(
        url="/login",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )

from .base import BaseDAO
from core.models import Task


class TasksDao(BaseDAO[Task]):
    model = Task

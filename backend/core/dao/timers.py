from core.models import Timer

from .base import BaseDAO


class TimersDAO(BaseDAO[Timer]):
    model = Timer

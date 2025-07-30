from .base import BaseDAO
from core.models import Timer


class TimersDAO(BaseDAO[Timer]):
    model = Timer

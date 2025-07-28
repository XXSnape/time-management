from core.models import User

from .base import BaseDAO


class UsersDao(BaseDAO[User]):
    model = User

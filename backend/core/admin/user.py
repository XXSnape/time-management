from sqladmin import ModelView

from core.models import User


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.username,
        User.telegram_id,
        User.is_admin,
    ]
    column_details_exclude_list = [User.password]
    can_delete = False

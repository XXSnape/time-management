"""empty message

Revision ID: 19af37632982
Revises: 7a2b34b923fc
Create Date: 2025-07-30 12:10:33.018432

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "19af37632982"
down_revision: Union[str, Sequence[str], None] = "7a2b34b923fc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "tracking",
        sa.Column("reminder_hour", sa.Integer(), nullable=False),
    )
    op.add_column(
        "tracking",
        sa.Column("habit_id", sa.Integer(), nullable=False),
    )
    op.create_unique_constraint(
        op.f("uq_tracking_reminder_date_reminder_hour_habit_id"),
        "tracking",
        ["reminder_date", "reminder_hour", "habit_id"],
    )
    op.create_foreign_key(
        op.f("fk_tracking_habit_id_habits"),
        "tracking",
        "habits",
        ["habit_id"],
        ["id"],
        ondelete="CASCADE",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        op.f("fk_tracking_habit_id_habits"),
        "tracking",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("uq_tracking_reminder_date_reminder_hour_habit_id"),
        "tracking",
        type_="unique",
    )
    op.drop_column("tracking", "habit_id")
    op.drop_column("tracking", "reminder_hour")
    # ### end Alembic commands ###

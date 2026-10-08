"""add users and exercise ownership

Revision ID: 36f61470c786
Revises: fd5f4b99257d
Create Date: 2026-10-06 18:56:58.883255
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "36f61470c786"
down_revision: Union[str, Sequence[str], None] = "fd5f4b99257d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )

    with op.batch_alter_table("exercises") as batch_op:
        batch_op.add_column(
            sa.Column(
                "owner_user_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_exercises_owner_user_id",
            "users",
            ["owner_user_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("exercises") as batch_op:
        batch_op.drop_constraint(
            "fk_exercises_owner_user_id",
            type_="foreignkey",
        )

        batch_op.drop_column("owner_user_id")

    op.drop_table("users")
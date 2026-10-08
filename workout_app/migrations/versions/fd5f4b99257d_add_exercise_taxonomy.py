"""add exercise taxonomy

Revision ID: fd5f4b99257d
Revises: 7349b6c1ecfc
Create Date: 2026-10-06 15:21:58.278683
"""
from typing import Sequence, Union

from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


revision: str = "fd5f4b99257d"
down_revision: Union[str, Sequence[str], None] = "7349b6c1ecfc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exercise_families",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "exercise_muscles",
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("muscle_group_id", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("PRIMARY", "SECONDARY", name="musclerole"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
        ),
        sa.ForeignKeyConstraint(
            ["muscle_group_id"],
            ["muscle_groups.id"],
        ),
        sa.PrimaryKeyConstraint(
            "exercise_id",
            "muscle_group_id",
        ),
    )

    # Batch mode lets SQLite rebuild the table in order to add
    # constraints that SQLite cannot ALTER onto an existing table.
    with op.batch_alter_table("exercises") as batch_op:
        batch_op.add_column(
            sa.Column(
                "exercise_type",
                sa.Enum(
                    "COMPOUND",
                    "ISOLATION",
                    name="exercisetype",
                ),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "family_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_foreign_key(
            "fk_exercises_family_id",
            "exercise_families",
            ["family_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("exercises") as batch_op:
        batch_op.drop_constraint(
            "fk_exercises_family_id",
            type_="foreignkey",
        )

        batch_op.drop_column("family_id")
        batch_op.drop_column("exercise_type")

    op.drop_table("exercise_muscles")
    op.drop_table("exercise_families")

    bind = op.get_bind()

    if bind.dialect.name == "postgresql":
        postgresql.ENUM(
            name="musclerole"
        ).drop(bind, checkfirst=True)

        postgresql.ENUM(
            name="exercisetype"
        ).drop(bind, checkfirst=True)
"""separate muscles from muscle groups

Revision ID: 97103dcb894e
Revises: 36f61470c786
Create Date: 2026-10-07 16:36:38.702162

"""
from typing import Sequence, Union

from sqlalchemy.dialects import postgresql

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '97103dcb894e'
down_revision: Union[str, Sequence[str], None] = '36f61470c786'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def muscle_role_enum():
    return postgresql.ENUM(
        "PRIMARY",
        "SECONDARY",
        name="musclerole",
        create_type=False,
    )


def role_column():
    return sa.Column(
        "role",
        muscle_role_enum()
        if op.get_bind().dialect.name == "postgresql"
        else sa.Enum("PRIMARY", "SECONDARY", name="musclerole"),
        nullable=False,
    )

def upgrade() -> None:
    op.create_table(
        "muscles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
    )

    op.drop_table("exercise_muscles")

    op.create_table(
        "exercise_muscles",
        sa.Column(
            "exercise_id",
            sa.Integer(),
            sa.ForeignKey("exercises.id"),
            primary_key=True,
        ),
        sa.Column(
            "muscle_id",
            sa.Integer(),
            sa.ForeignKey("muscles.id"),
            primary_key=True,
        ),
        role_column(),
    )


def downgrade() -> None:
    op.drop_table("exercise_muscles")

    op.create_table(
        "exercise_muscles",
        sa.Column(
            "exercise_id",
            sa.Integer(),
            sa.ForeignKey("exercises.id"),
            primary_key=True,
        ),
        sa.Column(
            "muscle_group_id",
            sa.Integer(),
            sa.ForeignKey("muscle_groups.id"),
            primary_key=True,
        ),
        role_column(),
    )

    op.drop_table("muscles")

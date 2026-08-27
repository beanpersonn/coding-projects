from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    categories: Mapped[List["Category"]] = relationship(
        back_populates="muscle_group"
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    weekly_quota: Mapped[int] = mapped_column(
        nullable=False
    )

    muscle_group_id: Mapped[int] = mapped_column(
        ForeignKey("muscle_groups.id"),
        nullable=False
    )

    muscle_group: Mapped["MuscleGroup"] = relationship(
        back_populates="categories"
    )

    exercises: Mapped[List["Exercise"]] = relationship(
        back_populates="category"
    )

class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"),
        nullable=False
    )

    category: Mapped["Category"] = relationship(
        back_populates="exercises"
    )
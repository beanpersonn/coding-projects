from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, String
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

    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="exercise"
    )

class TrainingWeek(Base):
    __tablename__ = "training_weeks"

    id: Mapped[int] = mapped_column(primary_key=True)

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",
        nullable=False
    )

    workout_days: Mapped[List["WorkoutDay"]] = relationship(
        back_populates="training_week",
        cascade="all, delete-orphan"
    )

class WorkoutDay(Base):
    __tablename__ = "workout_days"

    id: Mapped[int] = mapped_column(primary_key=True)

    training_week_id: Mapped[int] = mapped_column(
        ForeignKey("training_weeks.id"),
        nullable=False
    )

    day_number: Mapped[int] = mapped_column(
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    creation_method: Mapped[str] = mapped_column(
        String(20),
        default="manual",
        nullable=False
    )

    training_week: Mapped["TrainingWeek"] = relationship(
        back_populates="workout_days"
    )

    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        back_populates="workout_day",
        cascade="all, delete-orphan"
    )

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(primary_key=True)

    workout_day_id: Mapped[int] = mapped_column(
        ForeignKey("workout_days.id"),
        nullable=False
    )

    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id"),
        nullable=False
    )

    position: Mapped[int] = mapped_column(
        nullable=False
    )

    workout_day: Mapped["WorkoutDay"] = relationship(
        back_populates="workout_exercises"
    )

    exercise: Mapped["Exercise"] = relationship(
        back_populates="workout_exercises"
    )

    set_logs: Mapped[List["SetLog"]] = relationship(
        back_populates="workout_exercise",
        cascade="all, delete-orphan"
    )

class SetLog(Base):
    __tablename__ = "set_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    workout_exercise_id: Mapped[int] = mapped_column(
        ForeignKey("workout_exercises.id"),
        nullable=False
    )

    set_number: Mapped[int] = mapped_column(
        nullable=False
    )

    weight: Mapped[float] = mapped_column(
        nullable=False
    )

    reps: Mapped[int] = mapped_column(
        nullable=False
    )

    workout_exercise: Mapped["WorkoutExercise"] = relationship(
        back_populates="set_logs"
    )
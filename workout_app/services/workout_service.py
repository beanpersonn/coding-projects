from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import SessionLocal
from models import (
    TrainingWeek,
    WorkoutDay,
    WorkoutExercise,
    Exercise,
    Category
)

def get_current_training_week():
    session = SessionLocal()

    try:
        statement = (
            select(TrainingWeek)
            .where(TrainingWeek.status == "active")
            .order_by(TrainingWeek.start_date.desc())
        )

        training_week = session.scalar(statement)

        if training_week is None:
            return None

        return get_training_week(training_week.id)

    finally:
        session.close()

def get_training_week(week_id):
    session = SessionLocal()

    try:
        statement = (
            select(TrainingWeek)
            .where(TrainingWeek.id == week_id)
            .options(
                selectinload(TrainingWeek.workout_days)
                .selectinload(WorkoutDay.workout_exercises)
                .selectinload(WorkoutExercise.exercise)
                .selectinload(Exercise.category)
                .selectinload(Category.muscle_group)
            )
        )

        training_week = session.scalar(statement)

        if training_week is None:
            return None

        week = []

        sorted_days = sorted(
            training_week.workout_days,
            key=lambda day: day.day_number
        )

        for workout_day in sorted_days:
            day = []

            sorted_exercises = sorted(
                workout_day.workout_exercises,
                key=lambda item: item.position
            )

            for workout_exercise in sorted_exercises:
                exercise = workout_exercise.exercise

                day.append({
                    "exercise_id": exercise.id,
                    "exercise": exercise.name,
                    "category_id": exercise.category.id,
                    "category": exercise.category.name,
                    "muscle_group": exercise.category.muscle_group.name,
                })

            week.append(day)

        return week

    finally:
        session.close()

def save_generated_week(
    generated_week,
    start_date=None
):
    """
    Save a generated workout week to the database.

    generated_week is expected to be the list of days
    returned by services.randomizer.generate_week().
    """

    if start_date is None:
        start_date = date.today()

    session = SessionLocal()

    try:
        training_week = TrainingWeek(
            start_date=start_date,
            status="active"
        )

        session.add(training_week)
        session.flush()

        for day_number, day in enumerate(
            generated_week,
            start=1
        ):
            workout_day = WorkoutDay(
                training_week_id=training_week.id,
                day_number=day_number,
                name=f"Day {day_number}",
                creation_method="randomized"
            )

            session.add(workout_day)
            session.flush()

            for position, item in enumerate(
                day,
                start=1
            ):
                workout_exercise = WorkoutExercise(
                    workout_day_id=workout_day.id,
                    exercise_id=item["exercise_id"],
                    position=position
                )

                session.add(workout_exercise)

        session.commit()

        return training_week.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

#test block:
if __name__ == "__main__":
    week = get_current_training_week()

    if week is None:
        print("No active training week.")

    else:
        for day_number, day in enumerate(
            week,
            start=1
        ):
            print()
            print(f"DAY {day_number}")

            for position, item in enumerate(
                day,
                start=1
            ):
                print(
                    f"{position}. "
                    f"{item['exercise']} "
                    f"({item['muscle_group']} - "
                    f"{item['category']})"
                )
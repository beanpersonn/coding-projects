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

def add_workout_day(
    training_week_id,
    name,
    creation_method="manual"
):
    session = SessionLocal()

    try:
        training_week = session.get(
            TrainingWeek,
            training_week_id
        )

        if training_week is None:
            raise ValueError(
                f"Training week {training_week_id} does not exist."
            )

        statement = (
            select(WorkoutDay)
            .where(
                WorkoutDay.training_week_id
                == training_week_id
            )
            .order_by(
                WorkoutDay.day_number.desc()
            )
        )

        last_day = session.scalar(statement)

        if last_day is None:
            next_day_number = 1
        else:
            next_day_number = last_day.day_number + 1

        workout_day = WorkoutDay(
            training_week_id=training_week_id,
            day_number=next_day_number,
            name=name,
            creation_method=creation_method
        )

        session.add(workout_day)
        session.commit()

        return workout_day.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def add_exercise_to_workout_day(
    workout_day_id,
    exercise_id
):
    session = SessionLocal()

    try:
        workout_day = session.get(
            WorkoutDay,
            workout_day_id
        )

        if workout_day is None:
            raise ValueError(
                f"Workout day {workout_day_id} does not exist."
            )

        exercise = session.get(
            Exercise,
            exercise_id
        )

        if exercise is None:
            raise ValueError(
                f"Exercise {exercise_id} does not exist."
            )

        statement = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id
                == workout_day_id
            )
            .order_by(
                WorkoutExercise.position.desc()
            )
        )

        last_exercise = session.scalar(statement)

        if last_exercise is None:
            next_position = 1
        else:
            next_position = last_exercise.position + 1

        workout_exercise = WorkoutExercise(
            workout_day_id=workout_day_id,
            exercise_id=exercise_id,
            position=next_position
        )

        session.add(workout_exercise)
        session.commit()

        return workout_exercise.id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def get_active_exercises():
    session = SessionLocal()

    try:
        statement = (
            select(Exercise)
            .where(Exercise.active.is_(True))
            .options(
                selectinload(Exercise.category)
                .selectinload(Category.muscle_group)
            )
            .order_by(Exercise.name)
        )

        exercises = session.scalars(statement).all()

        return [
            {
                "id": exercise.id,
                "name": exercise.name,
                "category": exercise.category.name,
                "muscle_group": exercise.category.muscle_group.name,
            }
            for exercise in exercises
        ]

    finally:
        session.close()

def remove_exercise_from_workout_day(
    workout_exercise_id
):
    session = SessionLocal()

    try:
        workout_exercise = session.get(
            WorkoutExercise,
            workout_exercise_id
        )

        if workout_exercise is None:
            raise ValueError(
                f"Workout exercise "
                f"{workout_exercise_id} does not exist."
            )

        workout_day_id = (
            workout_exercise.workout_day_id
        )

        session.delete(workout_exercise)
        session.flush()

        statement = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id
                == workout_day_id
            )
            .order_by(
                WorkoutExercise.position
            )
        )

        remaining_exercises = (
            session.scalars(statement).all()
        )

        for position, exercise in enumerate(
            remaining_exercises,
            start=1
        ):
            exercise.position = position

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def move_workout_exercise(
    workout_exercise_id,
    direction
):
    session = SessionLocal()

    try:
        workout_exercise = session.get(
            WorkoutExercise,
            workout_exercise_id
        )

        if workout_exercise is None:
            raise ValueError(
                f"Workout exercise "
                f"{workout_exercise_id} does not exist."
            )

        if direction not in ("up", "down"):
            raise ValueError(
                "direction must be 'up' or 'down'."
            )

        workout_day_id = (
            workout_exercise.workout_day_id
        )

        current_position = (
            workout_exercise.position
        )

        if direction == "up":
            target_position = current_position - 1
        else:
            target_position = current_position + 1

        statement = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id
                == workout_day_id,
                WorkoutExercise.position
                == target_position
            )
        )

        other_exercise = session.scalar(
            statement
        )

        # Already at the top/bottom.
        if other_exercise is None:
            return

        other_exercise.position = (
            current_position
        )

        workout_exercise.position = (
            target_position
        )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

def move_workout_exercise(
    workout_exercise_id,
    direction
):
    session = SessionLocal()

    try:
        workout_exercise = session.get(
            WorkoutExercise,
            workout_exercise_id
        )

        if workout_exercise is None:
            raise ValueError(
                f"Workout exercise "
                f"{workout_exercise_id} does not exist."
            )

        if direction not in ("up", "down"):
            raise ValueError(
                "direction must be 'up' or 'down'."
            )

        workout_day_id = (
            workout_exercise.workout_day_id
        )

        current_position = (
            workout_exercise.position
        )

        if direction == "up":
            target_position = current_position - 1
        else:
            target_position = current_position + 1

        statement = (
            select(WorkoutExercise)
            .where(
                WorkoutExercise.workout_day_id
                == workout_day_id,
                WorkoutExercise.position
                == target_position
            )
        )

        other_exercise = session.scalar(
            statement
        )

        # Already at the top/bottom.
        if other_exercise is None:
            return

        other_exercise.position = (
            current_position
        )

        workout_exercise.position = (
            target_position
        )

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

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

        week = {
            "id": training_week.id,
            "start_date": training_week.start_date,
            "status": training_week.status,
            "days": []
        }

        sorted_days = sorted(
            training_week.workout_days,
            key=lambda day: day.day_number
        )

        for workout_day in sorted_days:
            day = {
                "id": workout_day.id,
                "day_number": workout_day.day_number,
                "name": workout_day.name,
                "creation_method": workout_day.creation_method,
                "exercises": []
            }

            sorted_exercises = sorted(
                workout_day.workout_exercises,
                key=lambda item: item.position
            )

            for workout_exercise in sorted_exercises:
                exercise = workout_exercise.exercise

                day["exercises"].append({
                    "workout_exercise_id": workout_exercise.id,
                    "exercise_id": exercise.id,
                    "exercise": exercise.name,
                    "category_id": exercise.category.id,
                    "category": exercise.category.name,
                    "muscle_group": exercise.category.muscle_group.name,
                    "position": workout_exercise.position
                })

            week["days"].append(day)

        return week

    finally:
        session.close()

def save_generated_week(
    generated_week,
    start_date=None,
    day_names=None
):
    if start_date is None:
        start_date = date.today()

    if day_names is None:
        day_names = [
            f"Day {number}"
            for number in range(1, len(generated_week) + 1)
        ]

    if len(day_names) != len(generated_week):
        raise ValueError(
            "day_names must contain one name "
            "for each generated workout day."
        )

    session = SessionLocal()

    try:
        training_week = TrainingWeek(
            start_date=start_date,
            status="active"
        )

        session.add(training_week)
        session.flush()

        for day_number, (day, day_name) in enumerate(
            zip(generated_week, day_names),
            start=1
        ):
            workout_day = WorkoutDay(
                training_week_id=training_week.id,
                day_number=day_number,
                name=day_name,
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
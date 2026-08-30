from flask import Flask, redirect, render_template, request, url_for

from services.randomizer import generate_week
from services.workout_service import (
    add_workout_day,
    get_current_training_week,
    save_generated_week,
    add_exercise_to_workout_day,
    get_active_exercises,
    )

app = Flask(__name__)

@app.route("/")
def home():
    week = get_current_training_week()
    exercises = get_active_exercises()

    return render_template(
        "week.html",
        week=week,
        exercises=exercises
    )

@app.route(
    "/workout-days/<int:workout_day_id>/add-exercise",
    methods=["POST"]
)
def add_exercise(workout_day_id):
    exercise_id = request.form.get(
        "exercise_id",
        type=int
    )

    if exercise_id is None:
        return redirect(
            url_for("home")
        )

    add_exercise_to_workout_day(
        workout_day_id=workout_day_id,
        exercise_id=exercise_id
    )

    return redirect(
        url_for("home")
    )

@app.route("/add-workout-day", methods=["POST"])
def add_new_workout_day():
    week = get_current_training_week()

    if week is None:
        return redirect(
            url_for("home")
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    if not name:
        return redirect(
            url_for("home")
        )

    add_workout_day(
        training_week_id=week["id"],
        name=name,
        creation_method="manual"
    )

    return redirect(
        url_for("home")
    )

@app.route("/generate-week", methods=["POST"])
def generate_new_week():
    generated_week = generate_week()

    save_generated_week(
        generated_week,
        day_names=[
            "Upper 1",
            "Upper 2",
            "Upper 3",
            "Upper 4"
        ]
    )

    return redirect(
        url_for("home")
    )

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )
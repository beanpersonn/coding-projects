from flask import Flask, redirect, render_template, url_for

from services.randomizer import generate_week
from services.workout_service import (
    get_current_training_week,
    save_generated_week
)


app = Flask(__name__)


@app.route("/")
def home():
    week = get_current_training_week()

    return render_template(
        "week.html",
        week=week
    )


@app.route("/generate-week", methods=["POST"])
def generate_new_week():
    generated_week = generate_week()

    save_generated_week(
        generated_week
    )

    return redirect(
        url_for("home")
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        port=5001
    )
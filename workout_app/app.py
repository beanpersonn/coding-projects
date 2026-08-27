from flask import Flask, render_template

from services.randomizer import generate_week

app = Flask(__name__)

@app.route("/")
def home():
    week = generate_week()

    return render_template(
        "week.html",
        week=week
    )

if __name__ == "__main__":
    app.run(debug=True)
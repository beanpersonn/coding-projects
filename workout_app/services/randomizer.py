import random
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database import SessionLocal
from models import Category, Exercise

DAY_SIZES = [5, 5, 4, 4]

CATEGORY_WEEKLY_QUOTAS = {
    "Lats / Pulldowns": 2,
    "Rows": 2,
    "Shrug": 1,

    "Incline Press": 1,
    "Press": 1,
    "Fly": 1,

    "Lateral Raises": 2,
    "Rear Delts": 2,
    "Overhead Press": 1,

    "Biceps": 2,
    "Triceps": 2,
    "Finisher": 1,
}

def load_categories(session):
    """
    Load every category and its active exercises from the database.

    Each Category already knows:
    - its weekly quota
    - its MuscleGroup
    - its Exercises
    """
    statement = (
        select(Category)
        .options(
            selectinload(Category.muscle_group),
            selectinload(Category.exercises)
        )
        .order_by(Category.id)
    )
    return session.scalars(statement).all()

def select_weekly_exercises(categories):
    selected = []

    for category in categories:
        weekly_quota = CATEGORY_WEEKLY_QUOTAS.get(
            category.name,
            0
        )

        if weekly_quota == 0:
            continue

        active_exercises = [
            exercise
            for exercise in category.exercises
            if exercise.active
        ]

        if len(active_exercises) < weekly_quota:
            raise ValueError(
                f"Category '{category.name}' requires "
                f"{weekly_quota} exercises per week, "
                f"but only {len(active_exercises)} active exercises "
                f"are available."
            )

        choices = random.sample(
            active_exercises,
            weekly_quota
        )

        for exercise in choices:
            selected.append({
                "exercise_id": exercise.id,
                "exercise": exercise.name,
                "category_id": category.id,
                "category": category.name,
                "muscle_group": category.muscle_group.name,
            })

    return selected

def score_week(days):
    """
    Give each candidate weekly layout a score.

    Lower score = better distribution.

    This does NOT affect which exercises were selected.
    It only affects how those exercises are spread over
    the four training days.
    """
    score = 0
    # --------------------------------------------------
    # 1. Avoid placing two exercises from the same
    #    category on the same day.
    #
    # Example:
    # Don't put both selected lat exercises on Day 1.
    # --------------------------------------------------
    for day in days:
        category_counts = Counter(
            item["category_id"]
            for item in day
        )
        for count in category_counts.values():
            if count > 1:
                score += (count - 1) * 25
    # --------------------------------------------------
    # 2. Mildly discourage stacking too many exercises
    #    from one broad muscle group on the same day.
    #
    # Example:
    # 3+ shoulder exercises on one day gets penalized.
    # --------------------------------------------------
    for day in days:
        muscle_group_counts = Counter(
            item["muscle_group"]
            for item in day
        )
        for count in muscle_group_counts.values():
            if count >= 3:
                score += (count - 2) * 3
    return score

def distribute_week(selected):
    """
    Take the valid 18-exercise weekly pool and distribute it
    into the required:

        Day 1: 5
        Day 2: 5
        Day 3: 4
        Day 4: 4

    We try many random layouts and retain the best-balanced one.
    """
    best_days = None
    best_score = float("inf")
    for _ in range(3000):
        pool = selected.copy()
        random.shuffle(pool)
        days = []
        index = 0
        for size in DAY_SIZES:
            days.append(
                pool[index:index + size]
            )
            index += size
        score = score_week(days)
        if score < best_score:
            best_score = score
            best_days = days
            # Zero means there are no category collisions
            # or excessive broad-muscle-group stacking.
            if best_score == 0:
                break
    return best_days

def validate_week(days, categories):
    """
    Final safety check.

    The generator should never return a week that violates
    our programming rules.
    """
    flattened = [
        item
        for day in days
        for item in day
    ]
    # --------------------------------------------
    # Correct day distribution
    # --------------------------------------------
    assert [len(day) for day in days] == DAY_SIZES
    # --------------------------------------------
    # Correct total number of weekly exercises
    # --------------------------------------------
    required_total = sum(
        CATEGORY_WEEKLY_QUOTAS.values()
    )      
    assert len(flattened) == required_total
    # --------------------------------------------
    # No exercise can appear twice in one week
    # --------------------------------------------
    exercise_ids = [
        item["exercise_id"]
        for item in flattened
    ]
    assert len(exercise_ids) == len(set(exercise_ids))
    # --------------------------------------------
    # Exact category quotas
    # --------------------------------------------
    actual_counts = Counter(
        item["category_id"]
        for item in flattened
    )
    for category in categories:
        expected_quota = CATEGORY_WEEKLY_QUOTAS.get(
            category.name,
            0
        )

    assert (
        actual_counts[category.id]
        == expected_quota
    )

def generate_week():
    """
    Main public function.

    Flask will eventually call this function whenever
    we want to generate a new training week.
    """
    session = SessionLocal()
    try:
        categories = load_categories(session)
        selected = select_weekly_exercises(
            categories
        )
        days = distribute_week(
            selected
        )
        validate_week(
            days,
            categories
        )
        return days
    finally:

        session.close()

def print_week(days):
    """
    Temporary console output.

    Later Flask/HTML will replace this, but it's useful
    for testing our database-backed generator first.
    """
    print()
    print("=" * 65)
    print("                 UPPER BODY RANDOMIZER")
    print("=" * 65)
    for day_number, day in enumerate(
        days,
        start=1
    ):
        print()
        print(
            f"DAY {day_number} "
            f"— {len(day)} exercises"
        )
        print("-" * 65)
        for number, item in enumerate(
            day,
            start=1
        ):
            print(
                f"{number}. "
                f"{item['exercise']} "
                f"({item['muscle_group']} - "
                f"{item['category']})"
            )
    print()

    #validation section
    print()
    print("WEEKLY VERIFICATION")
    print("-" * 65)

    category_counts = Counter(
        item["category"]
        for day in days
        for item in day
    )

    for category, count in sorted(
        category_counts.items()
    ):
        print(
            f"{category:<20} "
            f"{count}"
        )
    print("=" * 65)

if __name__ == "__main__":
    week = generate_week()
    print_week(week)
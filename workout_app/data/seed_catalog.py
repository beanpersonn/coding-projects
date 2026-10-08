from sqlalchemy import select

from database import SessionLocal
from models import (
    MuscleGroup,
    Muscle,
    Category,
    ExerciseFamily,
    Exercise,
    ExerciseMuscle,
    ExerciseType,
    MuscleRole,
)

# Broad groups used for browsing exercises.
# Categories are nested under these groups.
CATEGORIES = {
    "Chest": [
        "Chest Press",
        "Incline Press",
        "Chest Fly",
    ],
    "Back": [
        "Vertical Pull",
        "Row",
        "Pullover",
        "Shrug",
    ],
    "Shoulders": [
        "Overhead Press",
        "Lateral Raise",
        "Rear Delt",
    ],
    "Arms": [
        "Biceps",
        "Triceps",
    ],
    "Legs": [
        "Squat",
        "Leg Press",
        "Single-Leg",
        "Hip Hinge",
        "Leg Extension",
        "Leg Curl",
        "Hip Thrust",
        "Calves",
        "Adductors",
        "Abductors",
    ],
}

# Anatomical muscles used for primary/secondary targeting.
MUSCLES = [
    "Pectorals",
    "Lats",
    "Upper Back",
    "Trapezius",
    "Erector Spinae",
    "Anterior Deltoids",
    "Lateral Deltoids",
    "Posterior Deltoids",
    "Biceps",
    "Brachialis",
    "Brachioradialis",
    "Triceps",
    "Quads",
    "Hamstrings",
    "Glutes",
    "Calves",
    "Adductors",
    "Abductors",
]

# Each family contains specific, independently trackable exercises.
#
# Format:
# (exercise name, type, primary muscles, secondary muscles)
CATALOG = {
    "Chest Press": {
        "Bench Press": [
            ("Barbell Bench Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
            ("Dumbbell Bench Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
            ("Machine Chest Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
        ],
    },
    "Incline Press": {
        "Incline Bench Press": [
            ("Incline Barbell Bench Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
            ("Incline Dumbbell Bench Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
            ("Incline Machine Press", "COMPOUND", ["Pectorals"], ["Triceps", "Anterior Deltoids"]),
        ],
    },
    "Chest Fly": {
        "Chest Fly": [
            ("Cable Chest Fly", "ISOLATION", ["Pectorals"], []),
            ("Dumbbell Chest Fly", "ISOLATION", ["Pectorals"], []),
            ("Pec Deck", "ISOLATION", ["Pectorals"], []),
        ],
    },
    "Vertical Pull": {
        "Pull-Up": [
            ("Pull-Up", "COMPOUND", ["Lats"], ["Biceps", "Upper Back"]),
            ("Chin-Up", "COMPOUND", ["Lats"], ["Biceps", "Upper Back"]),
        ],
        "Lat Pulldown": [
            ("Lat Pulldown", "COMPOUND", ["Lats"], ["Biceps", "Upper Back"]),
            ("Neutral-Grip Lat Pulldown", "COMPOUND", ["Lats"], ["Biceps", "Upper Back"]),
            ("Machine Lat Pulldown", "COMPOUND", ["Lats"], ["Biceps", "Upper Back"]),
        ],
    },
    "Row": {
        "Row": [
            ("Barbell Row", "COMPOUND", ["Upper Back", "Lats"], ["Biceps"]),
            ("Dumbbell Row", "COMPOUND", ["Upper Back", "Lats"], ["Biceps"]),
            ("Seated Cable Row", "COMPOUND", ["Upper Back", "Lats"], ["Biceps"]),
            ("Chest-Supported Row", "COMPOUND", ["Upper Back", "Lats"], ["Biceps"]),
            ("Machine Row", "COMPOUND", ["Upper Back", "Lats"], ["Biceps"]),
        ],
    },
    "Pullover": {
        "Pullover": [
            ("Cable Pullover", "ISOLATION", ["Lats"], []),
            ("Machine Pullover", "ISOLATION", ["Lats"], []),
        ],
    },
    "Shrug": {
        "Shrug": [
            ("Barbell Shrug", "ISOLATION", ["Trapezius"], []),
            ("Dumbbell Shrug", "ISOLATION", ["Trapezius"], []),
            ("Machine Shrug", "ISOLATION", ["Trapezius"], []),
        ],
    },
    "Overhead Press": {
        "Shoulder Press": [
            ("Barbell Overhead Press", "COMPOUND", ["Anterior Deltoids"], ["Triceps", "Lateral Deltoids"]),
            ("Dumbbell Shoulder Press", "COMPOUND", ["Anterior Deltoids"], ["Triceps", "Lateral Deltoids"]),
            ("Machine Shoulder Press", "COMPOUND", ["Anterior Deltoids"], ["Triceps", "Lateral Deltoids"]),
        ],
    },
    "Lateral Raise": {
        "Lateral Raise": [
            ("Dumbbell Lateral Raise", "ISOLATION", ["Lateral Deltoids"], []),
            ("Cable Lateral Raise", "ISOLATION", ["Lateral Deltoids"], []),
            ("Machine Lateral Raise", "ISOLATION", ["Lateral Deltoids"], []),
        ],
    },
    "Rear Delt": {
        "Rear Delt Fly": [
            ("Reverse Pec Deck", "ISOLATION", ["Posterior Deltoids"], ["Upper Back"]),
            ("Cable Rear Delt Fly", "ISOLATION", ["Posterior Deltoids"], ["Upper Back"]),
            ("Dumbbell Rear Delt Fly", "ISOLATION", ["Posterior Deltoids"], ["Upper Back"]),
        ],
        "Face Pull": [
            ("Face Pull", "ISOLATION", ["Posterior Deltoids"], ["Upper Back"]),
        ],
    },
    "Biceps": {
        "Curl": [
            ("Barbell Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Dumbbell Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Cable Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Hammer Curl", "ISOLATION", ["Brachialis", "Brachioradialis"], ["Biceps"]),
            ("Incline Dumbbell Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
        ],
        "Preacher Curl": [
            ("Barbell Preacher Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Dumbbell Preacher Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Machine Preacher Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
            ("Plate-Loaded Preacher Curl", "ISOLATION", ["Biceps"], ["Brachialis"]),
        ],
    },
    "Triceps": {
        "Triceps Pushdown": [
            ("Cable Bar Triceps Pushdown", "ISOLATION", ["Triceps"], []),
            ("Cable Rope Triceps Pushdown", "ISOLATION", ["Triceps"], []),
            ("Cable Single-Arm Triceps Pushdown", "ISOLATION", ["Triceps"], [])
        ],
        "Overhead Triceps Extension": [
            ("Overhead Cable Triceps Extension", "ISOLATION", ["Triceps"], []),
            ("Dumbbell Overhead Triceps Extension", "ISOLATION", ["Triceps"], []),
        ],
        "Skull Crusher": [
            ("Skull Crusher", "ISOLATION", ["Triceps"], []),
        ],
    },
    "Squat": {
        "Squat": [
            ("Barbell Back Squat", "COMPOUND", ["Quads", "Glutes"], ["Hamstrings"]),
            ("Barbell Front Squat", "COMPOUND", ["Quads", "Glutes"], []),
            ("Goblet Squat", "COMPOUND", ["Quads", "Glutes"], []),
            ("Hack Squat", "COMPOUND", ["Quads", "Glutes"], []),
            ("Pendulum Squat", "COMPOUND", ["Quads", "Glutes"], [])
        ],
    },
    "Leg Press": {
        "Leg Press": [
            ("45-Degree Leg Press", "COMPOUND", ["Quads", "Glutes"], []),
            ("Horizontal Leg Press", "COMPOUND", ["Quads", "Glutes"], []),
        ],
    },
    "Single-Leg": {
        "Split Squat": [
            ("Bulgarian Split Squat", "COMPOUND", ["Quads", "Glutes"], []),
        ],
        "Lunge": [
            ("Walking Lunge", "COMPOUND", ["Quads", "Glutes"], []),
            ("Reverse Lunge", "COMPOUND", ["Quads", "Glutes"], []),
        ],
        "Step-Up": [
            ("Step-Up", "COMPOUND", ["Quads", "Glutes"], []),
        ],
    },
    "Hip Hinge": {
        "Romanian Deadlift": [
            ("Romanian Deadlift", "COMPOUND", ["Hamstrings", "Glutes"], ["Erector Spinae"]),
        ],
        "Good Morning": [
            ("Good Morning", "COMPOUND", ["Hamstrings", "Glutes"], ["Erector Spinae"]),
        ],
    },
    "Leg Extension": {
        "Leg Extension": [
            ("Leg Extension", "ISOLATION", ["Quads"], []),
        ],
    },
    "Leg Curl": {
        "Leg Curl": [
            ("Seated Leg Curl", "ISOLATION", ["Hamstrings"], []),
            ("Lying Leg Curl", "ISOLATION", ["Hamstrings"], []),
            ("Standing Leg Curl", "ISOLATION", ["Hamstrings"], []),
        ],
    },
    "Hip Thrust": {
        "Hip Thrust": [
            ("Barbell Hip Thrust", "COMPOUND", ["Glutes"], ["Hamstrings"]),
            ("Machine Hip Thrust", "COMPOUND", ["Glutes"], ["Hamstrings"]),
        ],
        "Glute Bridge": [
            ("Glute Bridge", "COMPOUND", ["Glutes"], ["Hamstrings"]),
        ],
    },
    "Calves": {
        "Calf Raise": [
            ("Standing Calf Raise", "ISOLATION", ["Calves"], []),
            ("Seated Calf Raise", "ISOLATION", ["Calves"], []),
            ("Leg Press Calf Raise", "ISOLATION", ["Calves"], []),
        ],
    },
    "Adductors": {
        "Hip Adduction": [
            ("Hip Adduction Machine", "ISOLATION", ["Adductors"], []),
        ],
    },
    "Abductors": {
        "Hip Abduction": [
            ("Hip Abduction Machine", "ISOLATION", ["Abductors"], []),
        ],
    },
}


def get_or_create(session, model, **kwargs):
    instance = session.scalar(
        select(model).filter_by(**kwargs)
    )

    if instance is None:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()

    return instance


def seed_catalog():
    session = SessionLocal()

    try:
        categories = {}

        for group_name, category_names in CATEGORIES.items():
            group = get_or_create(
                session,
                MuscleGroup,
                name=group_name,
            )

            for category_name in category_names:
                category = get_or_create(
                    session,
                    Category,
                    name=category_name,
                    muscle_group_id=group.id,
                )
                categories[category_name] = category

        muscles = {
            name: get_or_create(session, Muscle, name=name)
            for name in MUSCLES
        }

        for category_name, families in CATALOG.items():
            category = categories[category_name]

            for family_name, exercises in families.items():
                family = get_or_create(
                    session,
                    ExerciseFamily,
                    name=family_name,
                )

                for name, exercise_type, primary, secondary in exercises:
                    exercise = session.scalar(
                        select(Exercise).where(Exercise.name == name)
                    )

                    if exercise is not None:
                        if exercise.owner_user_id is not None:
                            raise ValueError(
                                f"Catalog exercise conflicts with custom exercise: {name}"
                            )
                        continue

                    exercise = Exercise(
                        name=name,
                        category=category,
                        family=family,
                        exercise_type=ExerciseType[exercise_type],
                        owner_user_id=None,
                        active=True,
                    )
                    session.add(exercise)
                    session.flush()

                    for muscle_name in primary:
                        session.add(
                            ExerciseMuscle(
                                exercise_id=exercise.id,
                                muscle_id=muscles[muscle_name].id,
                                role=MuscleRole.PRIMARY,
                            )
                        )

                    for muscle_name in secondary:
                        session.add(
                            ExerciseMuscle(
                                exercise_id=exercise.id,
                                muscle_id=muscles[muscle_name].id,
                                role=MuscleRole.SECONDARY,
                            )
                        )

        session.commit()
        print("Generic exercise catalog seeded successfully.")

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    seed_catalog()
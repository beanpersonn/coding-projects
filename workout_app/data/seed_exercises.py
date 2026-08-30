from sqlalchemy import select

from database import SessionLocal
from models import MuscleGroup, Category, Exercise

EXERCISE_DATA = {
    "Back": {
        "Lats / Pulldowns": {
            "exercises": [
                "Pull ups",
                "ISO pulldown (PL, sideways sit)",
                "Lat pull down (PL)",
                "Lat pullover machine",
                "Lat pulldown wide grip",
                "Lat pulldown narrow grip",
                "Diverging lat pull down machine",
                "ISO high row (PL)",
            ],
        },

        "Rows": {
            "exercises": [
                "Seated cable row narrow grip",
                "Seated cable row wide grip",
                "ISO chest supported row (PL)",
                "MTS row machine",
                "Seated row machine (horizontal grip)",
                "Machine row (vertical grip)",
            ],
        },

        "Shrug": {
            "exercises": [
                "shrugs (PL)",
            ],
        },
    },

    "Chest": {
        "Incline Press": {
            "exercises": [
                "Incline DB",
                "ISO incline press (PL)",
                "Incline bench",
            ],
        },

        "Press": {
            "exercises": [
                "Flat bench DB",
                "ISO press (PL)",
                "Converging press machine",
                "ISO horizontal press (PL)",
                "bench press",
            ],
        },

        "Fly": {
            "exercises": [
                "Cable fly",
                "pec deck",
                "elbow fly machine",
            ],
        },
    },

    "Shoulders": {
        "Lateral Raises": {
            "exercises": [
                "lateral raises (DB)",
                "ISO cable lateral raises",
                "machine lateral raises",
            ],
        },

        "Rear Delts": {
            "exercises": [
                "rear delt fly pec deck",
                "ISO cable rear delt fly",
                "face pulls",
                "rear delt fly (DB)",
            ],
        },

        "Overhead Press": {
            "exercises": [
                "overhead press (DB)",
                "overhead press machine (PL)",
                "overhead press machine",
            ],
        },
    },

    "Arms": {
        "Biceps": {
            "exercises": [
                "rope cable hammer curls",
                "incline bench DB curls",
                "MTS single arm biceps curl",
                "Machine preacher curl",
                "Machine biceps curl (sandy)",
                "Machine biceps curl (precor)",
                "single arm cable curl",
                "machine preacher curl (PL)",
                "“arm curl” idk what this is tbh probably a specific machine",
            ],
        },

        "Triceps": {
            "exercises": [
                "rope cable extension",
                "single arm cable extension",
                "MTS single arm extension",
                "triceps extension machine (precor)",
                "bar cable extension",
            ],
        },

        "Finisher": {
            "exercises": [
                "superset finisher",
            ],
        },
    },

        "Legs": {
            "Quads": {
                "exercises": [
                    "Leg extension",
                    "ISO leg extension (PL)",
                    "ISO leg extension machine",
                ],
            },

            "Hamstrings": {
                "exercises": [
                    "Seated leg curl",
                    "Lying leg curl",
                    "Romanian deadlift",
                ],
            },

            "Glutes": {
                "exercises": [
                    "Hip thrust",
                ],
            },

            "Compound Lift": {
                "exercises": [
                    "Leg press",
                    "Squat press",
                    "V-Squat",
                    "Pendulum Squat",
                    "Barbell back squat",
                    "Bulgarian split squat",
                ],
            },

            "Calves": {
                "exercises": [
                    "Standing calf raise",
                    "Seated calf raise",
                ],
            },

            "Adductors": {
                "exercises": [
                    "Hip adduction machine",
                ],
            },

            "Abductors": {
                "exercises": [
                    "Hip abduction machine",
                ],
            },
        },
    }

def get_or_create_muscle_group(session, name):
    muscle_group = session.scalar(
        select(MuscleGroup).where(
            MuscleGroup.name == name
        )
    )

    if muscle_group is None:
        muscle_group = MuscleGroup(name=name)
        session.add(muscle_group)
        session.flush()

        print(f"Created muscle group: {name}")
    else:
        print(f"Muscle group already exists: {name}")

    return muscle_group

def get_or_create_category(
    session,
    name,
    muscle_group
):
    category = session.scalar(
        select(Category).where(
            Category.name == name
        )
    )

    if category is None:
        category = Category(
            name=name,
            muscle_group=muscle_group
        )

        session.add(category)
        session.flush()

        print(
            f"  Created category: {name}"
        )

    else:
        print(f"  Category already exists: {name}")

    return category

def get_or_create_exercise(
    session,
    name,
    category
):
    exercise = session.scalar(
        select(Exercise).where(
            Exercise.name == name
        )
    )

    if exercise is None:
        exercise = Exercise(
            name=name,
            category=category,
            active=True
        )

        session.add(exercise)

        print(f"    Added exercise: {name}")
    else:
        print(f"    Exercise already exists: {name}")

    return exercise

def seed_database():
    session = SessionLocal()

    try:
        print()
        print("=" * 60)
        print("SEEDING WORKOUT DATABASE")
        print("=" * 60)

        for muscle_group_name, categories in EXERCISE_DATA.items():

            print()
            print(f"[{muscle_group_name}]")

            muscle_group = get_or_create_muscle_group(
                session,
                muscle_group_name
            )

            for category_name, category_data in categories.items():

                category = get_or_create_category(
                    session=session,
                    name=category_name,
                    muscle_group=muscle_group
                )

                for exercise_name in category_data["exercises"]:

                    get_or_create_exercise(
                        session=session,
                        name=exercise_name,
                        category=category
                    )

        session.commit()

        print()
        print("=" * 60)
        print("DATABASE SEEDED SUCCESSFULLY")
        print("=" * 60)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()

if __name__ == "__main__":
    seed_database()
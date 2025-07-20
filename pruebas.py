import random
import uuid
from datetime import datetime, timedelta

# Predefined list of exercises and muscle groups
exercises = [
    ("Bench Press", "Chest"),
    ("Squat", "Legs"),
    ("Deadlift", "Back"),
    ("Overhead Press", "Shoulders"),
    ("Barbell Row", "Back"),
    ("Lat Pulldown", "Back"),
    ("Leg Press", "Legs"),
    ("Bicep Curl", "Arms"),
    ("Tricep Extension", "Arms"),
    ("Plank", "Core")
]

# Generate SQL INSERT statements
sql_statements = []

# Exercise insert statements
exercise_ids = {}
for name, group in exercises:
    eid = str(uuid.uuid4())
    exercise_ids[name] = eid
    sql_statements.append(f"INSERT INTO exercise (id, name, muscle_group) VALUES ('{eid}', '{name}', '{group}');")

# Generate 100 users
user_ids = []
for i in range(100):
    phone = f"+519{random.randint(10000000, 99999999)}"
    user_ids.append(phone)
    sql_statements.append(f"INSERT INTO auth.users (id) VALUES ('{phone}');")

    # Create 1-3 workout sessions per user
    for _ in range(random.randint(1, 3)):
        session_id = str(uuid.uuid4())
        start_time = datetime.now() - timedelta(days=random.randint(1, 90))
        end_time = start_time + timedelta(minutes=random.randint(30, 90))
        sql_statements.append(
            f"INSERT INTO workout_session (id, user_id, started_at, ended_at) "
            f"VALUES ('{session_id}', '{phone}', '{start_time}', '{end_time}');"
        )

        # Add 3-5 series per session
        for set_number in range(1, random.randint(4, 6)):
            exercise = random.choice(exercises)[0]
            reps = random.choice([8, 10, 12, 15])
            weight = round(random.uniform(10.0, 100.0), 2)
            series_id = str(uuid.uuid4())
            sql_statements.append(
                f"INSERT INTO series (id, session_id, exercise_id, set_number, reps, weight) "
                f"VALUES ('{series_id}', '{session_id}', '{exercise_ids[exercise]}', {set_number}, {reps}, {weight});"
            )

sql_statements[:5]  # Preview first 5 statements

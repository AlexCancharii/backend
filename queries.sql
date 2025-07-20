CREATE TABLE exercise (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL UNIQUE,
  muscle_group VARCHAR,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workout_session (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  started_at TIMESTAMP NOT NULL,
  ended_at TIMESTAMP,
  calories_burned FLOAT DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE series (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES workout_session(id) ON DELETE CASCADE,
  exercise_id UUID REFERENCES exercise(id),
  set_number INTEGER NOT NULL,
  reps INTEGER NOT NULL,
  weight NUMERIC(5,2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
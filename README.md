# NeuroLearn AI - Backend (Phase 3)

Flask REST API for the NeuroLearn AI project. Handles registration/login (JWT),
subjects/topics, quiz questions, quiz submission, performance aggregation, and
difficulty prediction (rule-based for now, swappable with the Phase 2 ML model).

## 1. Prerequisites

- Python 3.10+
- PostgreSQL installed and running (or skip this and it'll use SQLite automatically for local testing)

## 2. Setup

```bash
cd neurolearn_backend

# create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# install dependencies
pip install -r requirements.txt

# create your .env file
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Open `.env` and set `DATABASE_URL` to your PostgreSQL connection string, and
change `JWT_SECRET_KEY` to any random long string. If you don't set
`DATABASE_URL`, the app falls back to a local SQLite file automatically
(useful for quick testing before Postgres is set up).

### Create the PostgreSQL database (if using Postgres)

```sql
CREATE DATABASE neurolearn_db;
```

Tables are created automatically on first run (`db.create_all()` in `app.py`)
so you do NOT need to write CREATE TABLE statements manually.

## 3. Add sample data (optional but recommended)

```bash
python seed_data.py
```

This adds 1 subject (Computer Science), 2 topics (Recursion, Loops), and 3
sample MCQ questions so you have something to test with immediately.

## 4. Run the server

```bash
python app.py
```

Server runs at `http://localhost:5000`. Test it's alive:

```bash
curl http://localhost:5000/api/health
```

## 5. API Reference

| Method | Endpoint | Auth? | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Create a student account |
| POST | `/api/auth/login` | No | Login, returns JWT token |
| GET | `/api/subjects` | Yes | List all subjects |
| GET | `/api/subjects/<id>/topics` | Yes | List topics in a subject |
| GET | `/api/quiz/topic/<topic_id>/questions` | Yes | Get quiz questions (no answers included) |
| POST | `/api/quiz/submit` | Yes | Submit answers, get score + difficulty prediction |
| GET | `/api/quiz/history/<topic_id>` | Yes | Past attempts for a topic |
| GET | `/api/dashboard/me` | Yes | All topics with performance + predicted difficulty |

For protected routes, add header: `Authorization: Bearer <token>`

### Example: Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul Sharma","email":"rahul@example.com","password":"test123"}'
```

### Example: Submit a quiz

```bash
curl -X POST http://localhost:5000/api/quiz/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token_here>" \
  -d '{
    "topic_id": 1,
    "answers": [
      {"question_id": 1, "selected_option": "B", "time_taken_seconds": 15},
      {"question_id": 2, "selected_option": "A", "time_taken_seconds": 40}
    ]
  }'
```

Response includes `score`, and `performance` (accuracy, avg_response_time,
wrong_attempts, repeated_mistakes, improvement, predicted_difficulty).

## 6. How Phase 2 (ML model) will plug in

`ml/predictor.py` currently uses simple if/else rules so the whole app works
end-to-end today. Once the Decision Tree / Random Forest model is trained in
Phase 2, save it as `ml/difficulty_model.joblib` - `predictor.py` will
automatically detect and use it instead of the rules, with zero changes
needed anywhere else in the app.

## 7. Folder structure

```
neurolearn_backend/
├── app.py                  # Flask app factory + entry point
├── config.py                # Configuration from .env
├── extensions.py            # Shared SQLAlchemy instance
├── models.py                 # Student, Subject, Topic, Question, QuizAttempt, PerformanceRecord
├── auth.py                    # JWT generation + login_required decorator
├── seed_data.py                # Sample data for testing
├── routes/
│   ├── auth_routes.py           # /api/auth/*
│   ├── subject_routes.py        # /api/subjects/*
│   ├── quiz_routes.py           # /api/quiz/*
│   └── dashboard_routes.py      # /api/dashboard/*
├── ml/
│   └── predictor.py             # Difficulty prediction (rules now, ML model later)
├── requirements.txt
└── .env.example
```

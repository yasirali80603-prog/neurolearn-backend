"""
Run this once after setting up the database to add sample data,
so you have something to test the app with immediately:

    python seed_data.py
"""

from app import create_app
from extensions import db
from models import Subject, Topic, Question

app = create_app()

with app.app_context():
    if Subject.query.first():
        print("Sample data already exists. Skipping.")
    else:
        cs = Subject(name="Computer Science")
        db.session.add(cs)
        db.session.commit()

        recursion = Topic(subject_id=cs.id, name="Recursion")
        loops = Topic(subject_id=cs.id, name="Loops")
        db.session.add_all([recursion, loops])
        db.session.commit()

        questions = [
            Question(
                topic_id=recursion.id,
                question_text="What is the base case in recursion?",
                option_a="The first function call",
                option_b="The condition that stops further recursive calls",
                option_c="A loop inside the function",
                option_d="The return type of the function",
                correct_option="B",
            ),
            Question(
                topic_id=recursion.id,
                question_text="What happens if a recursive function has no base case?",
                option_a="It runs once and stops",
                option_b="It causes a stack overflow (infinite recursion)",
                option_c="It automatically returns 0",
                option_d="It converts to a loop",
                correct_option="B",
            ),
            Question(
                topic_id=loops.id,
                question_text="Which loop is guaranteed to execute at least once?",
                option_a="for loop",
                option_b="while loop",
                option_c="do-while loop",
                option_d="nested loop",
                correct_option="C",
            ),
        ]
        db.session.add_all(questions)
        db.session.commit()
        print("Sample data added: 1 subject, 2 topics, 3 questions.")

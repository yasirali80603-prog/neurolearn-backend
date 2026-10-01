from datetime import datetime
from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    quiz_attempts = db.relationship("QuizAttempt", backref="student", lazy=True)
    performance_records = db.relationship("PerformanceRecord", backref="student", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    topics = db.relationship("Topic", backref="subject", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)

    questions = db.relationship("Question", backref="topic", lazy=True)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "subject_id": self.subject_id}


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'

    def to_dict(self, include_answer=False):
        data = {
            "id": self.id,
            "topic_id": self.topic_id,
            "question_text": self.question_text,
            "options": {
                "A": self.option_a,
                "B": self.option_b,
                "C": self.option_c,
                "D": self.option_d,
            },
        }
        if include_answer:
            data["correct_option"] = self.correct_option
        return data


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    selected_option = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    time_taken_seconds = db.Column(db.Float, nullable=False)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "question_id": self.question_id,
            "selected_option": self.selected_option,
            "is_correct": self.is_correct,
            "time_taken_seconds": self.time_taken_seconds,
            "attempted_at": self.attempted_at.isoformat(),
        }


class PerformanceRecord(db.Model):
    """
    One row per (student, topic). Holds the aggregated features that get
    fed into the ML difficulty-prediction model, plus the latest prediction.
    """
    __tablename__ = "performance_records"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)

    accuracy = db.Column(db.Float, default=0.0)              # % correct answers
    avg_response_time = db.Column(db.Float, default=0.0)     # seconds
    wrong_attempts = db.Column(db.Integer, default=0)
    repeated_mistakes = db.Column(db.Integer, default=0)     # same question wrong more than once
    previous_score = db.Column(db.Float, default=0.0)
    improvement = db.Column(db.Float, default=0.0)           # change vs previous attempt

    predicted_difficulty = db.Column(db.String(10))          # 'Low' / 'Medium' / 'High'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("student_id", "topic_id", name="uq_student_topic"),)

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "topic_id": self.topic_id,
            "accuracy": self.accuracy,
            "avg_response_time": self.avg_response_time,
            "wrong_attempts": self.wrong_attempts,
            "repeated_mistakes": self.repeated_mistakes,
            "previous_score": self.previous_score,
            "improvement": self.improvement,
            "predicted_difficulty": self.predicted_difficulty,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

from flask import Blueprint, request, jsonify
from extensions import db
from models import Question, QuizAttempt, PerformanceRecord
from auth import login_required
from ml.predictor import predict_difficulty

quiz_bp = Blueprint("quiz_bp", __name__, url_prefix="/api/quiz")


@quiz_bp.route("/topic/<int:topic_id>/questions", methods=["GET"])
@login_required
def get_questions(topic_id):
    questions = Question.query.filter_by(topic_id=topic_id).all()
    # include_answer=False so the correct option is never sent to the app
    return jsonify([q.to_dict(include_answer=False) for q in questions]), 200


@quiz_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    """
    Body:
    {
      "topic_id": 1,
      "answers": [
        {"question_id": 5, "selected_option": "B", "time_taken_seconds": 12.4},
        ...
      ]
    }
    Saves each attempt, recalculates the student's performance features for
    this topic, asks the ML model for a difficulty prediction, and returns
    the quiz score plus the prediction.
    """
    data = request.get_json(silent=True) or {}
    topic_id = data.get("topic_id")
    answers = data.get("answers", [])
    student_id = request.student_id

    if not topic_id or not answers:
        return jsonify({"error": "topic_id and answers are required"}), 400

    correct_count = 0
    for ans in answers:
        question = Question.query.get(ans.get("question_id"))
        if not question:
            continue

        is_correct = question.correct_option.upper() == str(ans.get("selected_option", "")).upper()
        if is_correct:
            correct_count += 1

        attempt = QuizAttempt(
            student_id=student_id,
            topic_id=topic_id,
            question_id=question.id,
            selected_option=ans.get("selected_option"),
            is_correct=is_correct,
            time_taken_seconds=float(ans.get("time_taken_seconds", 0)),
        )
        db.session.add(attempt)

    db.session.commit()

    performance = _recalculate_performance(student_id, topic_id)

    return jsonify({
        "message": "Quiz submitted successfully",
        "score": f"{correct_count}/{len(answers)}",
        "performance": performance.to_dict(),
    }), 200


def _recalculate_performance(student_id, topic_id):
    """Recomputes aggregated features from all attempts and re-runs the ML prediction."""
    attempts = QuizAttempt.query.filter_by(student_id=student_id, topic_id=topic_id).all()
    total = len(attempts)

    record = PerformanceRecord.query.filter_by(student_id=student_id, topic_id=topic_id).first()
    if not record:
        record = PerformanceRecord(student_id=student_id, topic_id=topic_id)
        db.session.add(record)

    previous_accuracy = record.accuracy or 0.0

    if total > 0:
        correct = sum(1 for a in attempts if a.is_correct)
        accuracy = round((correct / total) * 100, 2)
        avg_time = round(sum(a.time_taken_seconds for a in attempts) / total, 2)
        wrong_attempts = total - correct

        # repeated mistake = same question answered incorrectly more than once
        wrong_question_counts = {}
        for a in attempts:
            if not a.is_correct:
                wrong_question_counts[a.question_id] = wrong_question_counts.get(a.question_id, 0) + 1
        repeated_mistakes = sum(1 for c in wrong_question_counts.values() if c > 1)

        record.accuracy = accuracy
        record.avg_response_time = avg_time
        record.wrong_attempts = wrong_attempts
        record.repeated_mistakes = repeated_mistakes
        record.previous_score = previous_accuracy
        record.improvement = round(accuracy - previous_accuracy, 2)

        record.predicted_difficulty = predict_difficulty({
            "accuracy": accuracy,
            "avg_response_time": avg_time,
            "wrong_attempts": wrong_attempts,
            "repeated_mistakes": repeated_mistakes,
            "improvement": record.improvement,
        })

    db.session.commit()
    return record


@quiz_bp.route("/history/<int:topic_id>", methods=["GET"])
@login_required
def quiz_history(topic_id):
    attempts = QuizAttempt.query.filter_by(
        student_id=request.student_id, topic_id=topic_id
    ).order_by(QuizAttempt.attempted_at.desc()).all()
    return jsonify([a.to_dict() for a in attempts]), 200

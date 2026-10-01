from flask import Blueprint, request, jsonify
from models import PerformanceRecord, Topic
from auth import login_required

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/me", methods=["GET"])
@login_required
def my_dashboard():
    """
    Returns every topic the student has attempted, with the latest
    performance features and predicted difficulty - this is what
    powers the Flutter progress dashboard / charts (fl_chart).
    """
    records = PerformanceRecord.query.filter_by(student_id=request.student_id).all()

    result = []
    for r in records:
        topic = Topic.query.get(r.topic_id)
        item = r.to_dict()
        item["topic_name"] = topic.name if topic else None
        result.append(item)

    # Simple summary counts, handy for a "topics needing attention" widget
    summary = {"Low": 0, "Medium": 0, "High": 0}
    for r in records:
        if r.predicted_difficulty in summary:
            summary[r.predicted_difficulty] += 1

    return jsonify({"topics": result, "summary": summary}), 200

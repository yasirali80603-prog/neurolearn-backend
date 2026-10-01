from flask import Blueprint, jsonify
from models import Subject, Topic
from auth import login_required

subject_bp = Blueprint("subject_bp", __name__, url_prefix="/api/subjects")


@subject_bp.route("", methods=["GET"])
@login_required
def list_subjects():
    subjects = Subject.query.all()
    return jsonify([s.to_dict() for s in subjects]), 200


@subject_bp.route("/<int:subject_id>/topics", methods=["GET"])
@login_required
def list_topics(subject_id):
    topics = Topic.query.filter_by(subject_id=subject_id).all()
    return jsonify([t.to_dict() for t in topics]), 200

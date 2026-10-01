from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Student
from auth import generate_token

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "name, email and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if Student.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    student = Student(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(student)
    db.session.commit()

    token = generate_token(student.id)
    return jsonify({"message": "Registered successfully", "token": token, "student": student.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    student = Student.query.filter_by(email=email).first()
    if not student or not check_password_hash(student.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(student.id)
    return jsonify({"message": "Login successful", "token": token, "student": student.to_dict()}), 200

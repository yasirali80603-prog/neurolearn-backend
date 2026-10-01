import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app


def generate_token(student_id):
    """Create a signed JWT for a student after successful login/registration."""
    payload = {
        "student_id": student_id,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=current_app.config["JWT_EXPIRY_HOURS"]),
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")
    return token


def decode_token(token):
    """Returns the payload dict if valid, raises jwt exceptions otherwise."""
    return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])


def login_required(f):
    """
    Decorator for protected routes. Expects header:
    Authorization: Bearer <token>
    Injects request.student_id for the route to use.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired, please login again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        request.student_id = payload["student_id"]
        return f(*args, **kwargs)

    return wrapper

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db

from routes.auth_routes import auth_bp
from routes.subject_routes import subject_bp
from routes.quiz_routes import quiz_bp
from routes.dashboard_routes import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)  # allows the Flutter app to call this API from a different origin
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(subject_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "NeuroLearn AI backend"}), 200

    with app.app_context():
        db.create_all()  # creates tables if they don't exist yet

    return app


import os

# Module-level app instance: gunicorn (used in production, e.g. on Render)
# imports this as "app:app". Local development still uses `python app.py`.
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

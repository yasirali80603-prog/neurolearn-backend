import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Central configuration for the NeuroLearn AI Flask backend.
    All values are read from environment variables (see .env.example).
    """

    # PostgreSQL database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///neurolearn_dev.db"  # fallback so the app can still run locally without Postgres
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT settings
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", 24))

    # Path where the trained ML model (from Phase 2) will be saved/loaded
    ML_MODEL_PATH = os.environ.get("ML_MODEL_PATH", "ml/difficulty_model.joblib")

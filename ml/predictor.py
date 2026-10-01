"""
Difficulty prediction module.

Right now this uses a simple rule-based heuristic so the API is fully
functional end-to-end. In Phase 2 we will train a Decision Tree / Random
Forest classifier on real quiz data and load it here with joblib instead -
the function signature (predict_difficulty) will stay exactly the same, so
nothing in quiz_routes.py needs to change.
"""

import os
import joblib
import pandas as pd

_MODEL = None
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "difficulty_model.joblib")


def _load_model():
    global _MODEL
    if _MODEL is None and os.path.exists(_MODEL_PATH):
        _MODEL = joblib.load(_MODEL_PATH)
    return _MODEL


def predict_difficulty(features: dict) -> str:
    """
    features = {
        "accuracy": float (0-100),
        "avg_response_time": float (seconds),
        "wrong_attempts": int,
        "repeated_mistakes": int,
        "improvement": float,
    }
    Returns one of: "Low", "Medium", "High"
    """
    model = _load_model()

    if model is not None:
        # Trained sklearn model path (used once Phase 2 is complete)
        row = pd.DataFrame([{
            "accuracy": features["accuracy"],
            "avg_response_time": features["avg_response_time"],
            "wrong_attempts": features["wrong_attempts"],
            "repeated_mistakes": features["repeated_mistakes"],
            "improvement": features["improvement"],
        }])
        return model.predict(row)[0]

    # --- Rule-based fallback (used until the trained model exists) ---
    accuracy = features.get("accuracy", 0)
    repeated_mistakes = features.get("repeated_mistakes", 0)
    avg_time = features.get("avg_response_time", 0)

    if accuracy >= 75 and repeated_mistakes == 0:
        return "Low"
    elif accuracy >= 45 or (repeated_mistakes <= 2 and avg_time < 60):
        return "Medium"
    else:
        return "High"

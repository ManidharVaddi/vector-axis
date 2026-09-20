import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from ml_features import get_checkin_history, build_feature_row, build_training_data

MIN_TRAINING_SAMPLES = 7

FEATURE_NAMES = ["is_weekend", "rolling_3", "rolling_7", "prev_day_outcome", "streak_length", "days_since_relapse"]

FEATURE_EXPLANATIONS = {
    "is_weekend": "Weekend timing",
    "rolling_3": "Your last 3 days of consistency",
    "rolling_7": "Your last 7 days of consistency",
    "prev_day_outcome": "Yesterday's outcome",
    "streak_length": "Your current streak length",
    "days_since_relapse": "Time since your last slip",
}


def _vectorize(feature_dict: dict) -> list[float]:
    is_weekend = 1.0 if feature_dict["day_of_week"] in (5, 6) else 0.0
    days_since_relapse_capped = min(feature_dict["days_since_relapse"], 14) / 14.0
    return [
        is_weekend,
        feature_dict["rolling_3"],
        feature_dict["rolling_7"],
        float(feature_dict["prev_day_outcome"]),
        min(feature_dict["streak_length"], 14) / 14.0,
        days_since_relapse_capped,
    ]


def predict_for_category(user_id: int, category_id: int, category_type: str) -> dict:
    history = get_checkin_history(user_id, category_id)

    if len(history) < MIN_TRAINING_SAMPLES:
        if history:
            recent = history[-min(5, len(history)):]
            prob_done = sum(e["done"] for e in recent) / len(recent)
        else:
            prob_done = 0.5

        prob_good = prob_done if category_type == "good" else (1 - prob_done)
        return {
            "mode": "heuristic",
            "prob_done_tomorrow": prob_done,
            "prob_good_outcome": prob_good,
            "explanation": f"Still learning your pattern ({len(history)}/{MIN_TRAINING_SAMPLES} check-ins collected) - using recent average until enough data exists to train a model.",
        }

    X_raw, y = build_training_data(history, min_prior=3)
    X_vectors = [_vectorize(f) for f in X_raw]

    if len(set(y)) < 2:
        prob_done = sum(y) / len(y)
        prob_good = prob_done if category_type == "good" else (1 - prob_done)
        return {
            "mode": "heuristic",
            "prob_done_tomorrow": prob_done,
            "prob_good_outcome": prob_good,
            "explanation": "Your behavior has been fully consistent so far - not enough variation yet to train a predictive model.",
        }

    X = np.array(X_vectors)
    y = np.array(y)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression()
    model.fit(X_scaled, y)

    tomorrow_features = build_feature_row(history, len(history))
    tomorrow_vector = np.array([_vectorize(tomorrow_features)])
    tomorrow_scaled = scaler.transform(tomorrow_vector)

    prob_done_tomorrow = float(model.predict_proba(tomorrow_scaled)[0][1])
    prob_good = prob_done_tomorrow if category_type == "good" else (1 - prob_done_tomorrow)

    coefs = model.coef_[0]
    top_idx = int(np.argmax(np.abs(coefs)))

    top_feature_name = FEATURE_NAMES[top_idx]
    top_feature_label = FEATURE_EXPLANATIONS[top_feature_name]
    coef_positive = coefs[top_idx] > 0

    if category_type == "good":
        direction = "increasing" if coef_positive else "decreasing"
        outcome_word = "sticking to this habit"
    else:
        direction = "decreasing" if coef_positive else "increasing"
        outcome_word = "avoiding this habit"

    explanation = f"{top_feature_label} is currently the strongest predictor here ({direction} your chances of {outcome_word})."
   
    return {
        "mode": "model",
        "prob_done_tomorrow": prob_done_tomorrow,
        "prob_good_outcome": prob_good,
        "explanation": explanation,
    }
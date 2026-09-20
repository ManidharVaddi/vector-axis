from categories import get_categories
from ml_predictor import predict_for_category
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def _cached_predict(user_id: int, category_id: int, category_type: str, cache_key: str) -> dict:
    """
    Wraps predict_for_category with caching. cache_key changes once per day,
    so predictions refresh daily instead of retraining on every single click.
    """
    return predict_for_category(user_id, category_id, category_type)


def get_top_suggestion(user_id: int) -> dict | None:
    categories = get_categories(user_id)
    if not categories:
        return None

    from time_utils import get_ist_today
    cache_key = get_ist_today().isoformat()

    results = []
    for cat in categories:
        prediction = _cached_predict(user_id, cat["id"], cat["type"], cache_key)
        results.append({
            "category_name": cat["name"],
            "category_type": cat["type"],
            "prob_good_outcome": prediction["prob_good_outcome"],
            "mode": prediction["mode"],
            "explanation": prediction["explanation"],
        })

    weakest = min(results, key=lambda r: r["prob_good_outcome"])

    pct = round(weakest["prob_good_outcome"] * 100)
    action_word = "sticking to" if weakest["category_type"] == "good" else "avoiding"

    if weakest["mode"] == "heuristic":
        message = (
            f"'{weakest['category_name']}' needs attention - your estimated success rate for "
            f"{action_word} it tomorrow is around {pct}%. {weakest['explanation']}"
        )
    else:
        message = (
            f"'{weakest['category_name']}' is your weakest link - the model predicts only a {pct}% "
            f"chance of {action_word} it tomorrow. {weakest['explanation']}"
        )

    weakest["message"] = message
    return weakest
from database import get_connection
from datetime import datetime


def get_checkin_history(user_id: int, category_id: int) -> list[dict]:
    """
    Returns this category's check-in history sorted oldest to newest:
    [{'date': date_obj, 'done': 0 or 1}, ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, done FROM checkins WHERE user_id = ? AND category_id = ? ORDER BY date ASC",
        (user_id, category_id),
    )
    rows = cur.fetchall()
    

    history = []
    for date_str, done in rows:
        history.append({
            "date": datetime.fromisoformat(date_str).date(),
            "done": int(done),
        })
    return history


def build_feature_row(history: list[dict], index: int) -> dict:
    """
    Builds a feature dict for predicting history[index]['done'], using only
    data strictly BEFORE index (no data leakage from the future).
    If index == len(history), this builds the feature row for TOMORROW's
    prediction, using the entire history as "the past".
    """
    prior = history[:index]

    if index < len(history):
        target_date = history[index]["date"]
        day_of_week = target_date.weekday()
    else:
        if prior:
            day_of_week = (prior[-1]["date"].weekday() + 1) % 7
        else:
            day_of_week = 0

    def rolling_avg(n):
        window = prior[-n:] if len(prior) >= 1 else []
        if not window:
            return 0.5
        return sum(e["done"] for e in window) / len(window)

    rolling_3 = rolling_avg(3)
    rolling_7 = rolling_avg(7)

    prev_day_outcome = prior[-1]["done"] if prior else 0.5

    streak_length = 0
    if prior:
        last_val = prior[-1]["done"]
        for entry in reversed(prior):
            if entry["done"] == last_val:
                streak_length += 1
            else:
                break

    days_since_relapse = len(prior)
    for i, entry in enumerate(reversed(prior)):
        if entry["done"] == 1:
            days_since_relapse = i
            break

    return {
        "day_of_week": day_of_week,
        "rolling_3": rolling_3,
        "rolling_7": rolling_7,
        "prev_day_outcome": prev_day_outcome,
        "streak_length": streak_length,
        "days_since_relapse": days_since_relapse,
    }


def build_training_data(history: list[dict], min_prior: int = 3) -> tuple[list[dict], list[int]]:
    """
    Converts history into (X, y) training examples.
    Skips the first `min_prior` entries since they don't have enough
    prior context to build meaningful features.
    """
    X = []
    y = []
    for i in range(min_prior, len(history)):
        features = build_feature_row(history, i)
        X.append(features)
        y.append(history[i]["done"])
    return X, y
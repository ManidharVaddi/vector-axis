"""
Generates demo/fallback visualization data using Vector Axis's own core logic
(the momentum engine's math) when a real user has no check-in history yet,
or when nobody is logged in.
"""

import random
from datetime import date, timedelta
from momentum import (
    GOOD_DONE_INCREMENT, GOOD_MISSED_DECREMENT,
    BAD_AVOIDED_DECREMENT, BAD_RELAPSE_INCREMENT, RELAPSE_RECOVERY_CAP,
    _clamp,
)

DEMO_CATEGORIES = [
    {"name": "Sample Good Habit", "type": "good"},
    {"name": "Sample Bad Habit", "type": "bad"},
]


def generate_demo_history(days: int = 30, seed: int = 7) -> dict:
    rng = random.Random(seed)

    good_score = 50.0
    bad_score = 50.0
    bad_relapse_active = False

    daily_scores = []
    weekly_ticks = []

    start = date.today() - timedelta(days=days - 1)

    for i in range(days):
        d = start + timedelta(days=i)

        good_done = rng.random() < min(0.5 + i * 0.01, 0.85)
        bad_done = rng.random() < 0.15

        if good_done:
            good_score = _clamp(good_score + GOOD_DONE_INCREMENT)
        else:
            good_score = _clamp(good_score - GOOD_MISSED_DECREMENT)

        if bad_done:
            bad_score = _clamp(bad_score + BAD_RELAPSE_INCREMENT)
            bad_relapse_active = True
        else:
            if bad_relapse_active:
                bad_score = _clamp(bad_score - RELAPSE_RECOVERY_CAP)
            else:
                bad_score = _clamp(bad_score - BAD_AVOIDED_DECREMENT)

        overall = _clamp((good_score + (100 - bad_score)) / 2)

        daily_scores.append({
            "date": d,
            "good_avg": good_score,
            "bad_avg": bad_score,
            "overall": overall,
        })

        weekly_ticks.append((d, "good", good_done))
        weekly_ticks.append((d, "bad", bad_done))

    weekly_summary = _aggregate_weekly(weekly_ticks)

    return {
        "categories": [
            {"name": "Sample Good Habit", "type": "good", "score": good_score},
            {"name": "Sample Bad Habit", "type": "bad", "score": bad_score},
        ],
        "daily_scores": daily_scores,
        "weekly_summary": weekly_summary,
    }


def _aggregate_weekly(ticks: list[tuple]) -> list[dict]:
    weeks = {}
    for d, cat_type, done in ticks:
        week_start = d - timedelta(days=d.weekday())
        key = week_start.isoformat()
        if key not in weeks:
            weeks[key] = {"week_start": week_start, "good_count": 0, "bad_count": 0}

        is_good_outcome = done if cat_type == "good" else (not done)
        if is_good_outcome:
            weeks[key]["good_count"] += 1
        else:
            weeks[key]["bad_count"] += 1

    return sorted(weeks.values(), key=lambda w: w["week_start"])
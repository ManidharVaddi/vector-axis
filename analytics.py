"""
Aggregates a REAL user's check-in history into the same shapes fallback_data.py
produces, so charts.py can consume either source through one consistent interface.
"""

from datetime import timedelta
from database import get_connection
from time_utils import get_ist_today


def get_weekly_summary(user_id: int, weeks_back: int = 5) -> list[dict]:
    today = get_ist_today()
    start = today - timedelta(weeks=weeks_back)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.date, cat.type, c.done
        FROM checkins c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = ? AND c.date >= ?
        ORDER BY c.date ASC
    """, (user_id, start.isoformat()))
    rows = cur.fetchall()
    

    weeks = {}
    for date_str, cat_type, done in rows:
        from datetime import date as date_cls
        d = date_cls.fromisoformat(date_str)
        week_start = d - timedelta(days=d.weekday())
        key = week_start.isoformat()
        if key not in weeks:
            weeks[key] = {"week_start": week_start, "good_count": 0, "bad_count": 0}

        is_good_outcome = bool(done) if cat_type == "good" else (not bool(done))
        if is_good_outcome:
            weeks[key]["good_count"] += 1
        else:
            weeks[key]["bad_count"] += 1

    return sorted(weeks.values(), key=lambda w: w["week_start"])


DAILY_TREND_MOVE_SCALE = 0.16
DAILY_TREND_MISSING_DECAY = 6.0


def get_daily_scores(user_id: int, days_back: int = 30) -> list[dict]:
    """
    Builds a CONTINUOUS running trend line (like a stock chart) - never has
    gaps. Each day either moves the line up (net good behavior), down (net
    bad behavior), or degrades it (no check-in submitted at all).
    """
    today = get_ist_today()
    start = today - timedelta(days=days_back - 1)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.date, cat.type, c.done
        FROM checkins c
        JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = ? AND c.date >= ?
        ORDER BY c.date ASC
    """, (user_id, start.isoformat()))
    rows = cur.fetchall()
    

    from collections import defaultdict
    by_date = defaultdict(list)
    for date_str, cat_type, done in rows:
        by_date[date_str].append((cat_type, bool(done)))

    daily_scores = []
    running_score = 50.0
    d = start

    while d <= today:
        date_str = d.isoformat()
        entries = by_date.get(date_str, [])

        if entries:
            good_entries = [done for t, done in entries if t == "good"]
            bad_entries = [done for t, done in entries if t == "bad"]
            good_rate = (sum(good_entries) / len(good_entries) * 100) if good_entries else None
            bad_avoid_rate = ((len(bad_entries) - sum(bad_entries)) / len(bad_entries) * 100) if bad_entries else None

            parts = [r for r in [good_rate, bad_avoid_rate] if r is not None]
            day_performance = sum(parts) / len(parts) if parts else 50.0

            delta = (day_performance - 50.0) * DAILY_TREND_MOVE_SCALE
            running_score = max(0.0, min(100.0, running_score + delta))
        else:
            good_rate = None
            bad_avoid_rate = None
            running_score = max(0.0, min(100.0, running_score - DAILY_TREND_MISSING_DECAY))

        daily_scores.append({
            "date": d,
            "good_avg": good_rate,
            "bad_avg": bad_avoid_rate,
            "overall": running_score,
        })
        d += timedelta(days=1)

    return daily_scores
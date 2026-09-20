from datetime import date
from database import get_connection

GOOD_DONE_INCREMENT = 5.0
GOOD_MISSED_DECREMENT = 3.0
BAD_AVOIDED_DECREMENT = 5.0
BAD_RELAPSE_INCREMENT = 10.0
RELAPSE_RECOVERY_CAP = 2.5

PENALTY_GOOD_DECAY = 8.0
PENALTY_BAD_RISE = 12.0
RELAPSE_RECOVERY_STREAK_NEEDED = 3


def _clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def apply_checkin(user_id: int, category_id: int, category_type: str, done: bool,
                   current_score: float, relapse_active: bool) -> tuple[float, bool]:
    if category_type == "good":
        if done:
            new_score = _clamp(current_score + GOOD_DONE_INCREMENT)
        else:
            new_score = _clamp(current_score - GOOD_MISSED_DECREMENT)
        return new_score, relapse_active
    else:
        if done:
            new_score = _clamp(current_score + BAD_RELAPSE_INCREMENT)
            return new_score, True
        else:
            if relapse_active:
                new_score = _clamp(current_score - RELAPSE_RECOVERY_CAP)
            else:
                new_score = _clamp(current_score - BAD_AVOIDED_DECREMENT)
            return new_score, relapse_active


def apply_penalty_day(current_score: float, category_type: str) -> float:
    if category_type == "good":
        return _clamp(current_score - PENALTY_GOOD_DECAY)
    else:
        return _clamp(current_score + PENALTY_BAD_RISE)


def submit_daily_checkin(user_id: int, ticks: dict[int, bool]) -> None:
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()

    for category_id, done in ticks.items():
        cur.execute(
            "SELECT type, score, relapse_penalty_active FROM categories WHERE id = ? AND user_id = ?",
            (category_id, user_id),
        )
        row = cur.fetchone()
        if row is None:
            continue
        category_type, current_score, relapse_active = row
        relapse_active = bool(relapse_active)

        new_score, new_relapse_active = apply_checkin(
            user_id, category_id, category_type, done, current_score, relapse_active
        )

        cur.execute(
            "UPDATE categories SET score = ?, relapse_penalty_active = ? WHERE id = ?",
            (new_score, int(new_relapse_active), category_id),
        )

        cur.execute(
            "INSERT OR REPLACE INTO checkins (user_id, category_id, date, done) VALUES (?, ?, ?, ?)",
            (user_id, category_id, today, int(done)),
        )

    cur.execute(
        "INSERT OR REPLACE INTO daily_activity (user_id, date, state) VALUES (?, ?, 'submitted')",
        (user_id, today),
    )

    conn.commit()
    

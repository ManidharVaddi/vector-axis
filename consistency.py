from datetime import timedelta
from database import get_connection
from time_utils import get_ist_today


def get_activity_log(user_id: int, days_back: int = 30) -> list[dict]:
    """
    Returns the last `days_back` days of activity state for this user, oldest first.
    """
    today = get_ist_today()
    start = today - timedelta(days=days_back - 1)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, state FROM daily_activity WHERE user_id = ? AND date >= ? ORDER BY date ASC",
        (user_id, start.isoformat()),
    )
    rows = {r[0]: r[1] for r in cur.fetchall()}
    

    log = []
    d = start
    while d <= today:
        date_str = d.isoformat()
        log.append({"date": d, "state": rows.get(date_str)})
        d += timedelta(days=1)
    return log


def get_current_streak(user_id: int) -> int:
    """
    Counts consecutive days ending today/yesterday with state == 'submitted'.
    """
    today = get_ist_today()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date, state FROM daily_activity WHERE user_id = ? ORDER BY date DESC",
        (user_id,),
    )
    rows = cur.fetchall()


    state_by_date = {r[0]: r[1] for r in rows}

    streak = 0
    check_date = today
    while True:
        date_str = check_date.isoformat()
        if state_by_date.get(date_str) == "submitted":
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break
    return streak
from datetime import date, timedelta
from database import get_connection
from momentum import apply_penalty_day
from time_utils import get_ist_today


def check_and_apply_missed_days(user_id: int, account_created_date: date) -> int:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT date FROM daily_activity WHERE user_id = ? ORDER BY date ASC",
        (user_id,),
    )
    existing_dates = {row[0] for row in cur.fetchall()}

    today = get_ist_today()
    penalties_applied = 0

    check_date = account_created_date
    while check_date < today:
        date_str = check_date.isoformat()
        if date_str not in existing_dates:
            cur.execute("SELECT id, type, score FROM categories WHERE user_id = ?", (user_id,))
            categories = cur.fetchall()

            for category_id, category_type, current_score in categories:
                new_score = apply_penalty_day(current_score, category_type)
                cur.execute("UPDATE categories SET score = ? WHERE id = ?", (new_score, category_id))

            cur.execute(
                "INSERT OR REPLACE INTO daily_activity (user_id, date, state) VALUES (?, ?, 'penalty_applied')",
                (user_id, date_str),
            )
            penalties_applied += 1
        check_date += timedelta(days=1)

    conn.commit()
    
    return penalties_applied


def has_checked_in_today(user_id: int) -> bool:
    today = get_ist_today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM daily_activity WHERE user_id = ? AND date = ? AND state = 'submitted'",
        (user_id, today),
    )
    row = cur.fetchone()
    
    return row is not None


def mark_app_opened_today(user_id: int) -> None:
    today = get_ist_today().isoformat()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO daily_activity (user_id, date, state) VALUES (?, ?, 'opened_no_submit')",
        (user_id, today),
    )
    conn.commit()
    
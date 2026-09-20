import bcrypt
from datetime import datetime
from database import get_connection


def register_user(username: str, password: str) -> tuple[bool, str]:
    """
    Creates a new user account with a hashed password.
    Returns (success: bool, message: str)
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        
        return False, "Username already taken."

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    created_at = datetime.utcnow().isoformat()

    cur.execute(
        "INSERT INTO users (username, password_hash, onboarding_complete, created_at) VALUES (?, ?, 0, ?)",
        (username, password_hash, created_at),
    )
    conn.commit()
    
    return True, "Account created successfully."


def login_user(username: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Validates login credentials.
    Returns (success: bool, message: str, user_dict: dict or None)
    """
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty.", None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, onboarding_complete, created_at FROM users WHERE username = ?",
        (username,),
    )
    row = cur.fetchone()
    

    if row is None:
        return False, "No account found with that username.", None

    user_id, db_username, password_hash, onboarding_complete, created_at = row

    if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        return False, "Incorrect password.", None

    user_dict = {
        "id": user_id,
        "username": db_username,
        "onboarding_complete": bool(onboarding_complete),
        "created_at": created_at,
    }

    return True,"Login Successful.",user_dict


def mark_onboarding_complete(user_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET onboarding_complete = 1 WHERE id = ?", (user_id,))
    conn.commit()
    
from database import get_connection


def save_categories(user_id: int, good_names: list[str], bad_names: list[str]) -> None:
    """
    Saves user-typed category names to the database, each starting at neutral score 50.0.
    Only called once, during onboarding. No default/sample categories are ever inserted.
    """
    conn = get_connection()
    cur = conn.cursor()

    for name in good_names:
        name = name.strip()
        if name:
            cur.execute(
                "INSERT INTO categories (user_id, name, type, score) VALUES (?, ?, 'good', 50.0)",
                (user_id, name),
            )

    for name in bad_names:
        name = name.strip()
        if name:
            cur.execute(
                "INSERT INTO categories (user_id, name, type, score) VALUES (?, ?, 'bad', 50.0)",
                (user_id, name),
            )

    conn.commit()



def get_categories(user_id: int) -> list[dict]:
    """
    Returns all categories for a user as a list of dicts:
    {id, name, type, score, relapse_penalty_active}
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, type, score, relapse_penalty_active FROM categories WHERE user_id = ?",
        (user_id,),
    )
    rows = cur.fetchall()
    

    return [
        {
            "id": r[0],
            "name": r[1],
            "type": r[2],
            "score": r[3],
            "relapse_penalty_active": bool(r[4]),
        }
        for r in rows
    ]
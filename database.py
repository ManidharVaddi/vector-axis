import os
from datetime import datetime
from dotenv import load_dotenv
import libsql
import streamlit as st

load_dotenv()

try:
    if "TURSO_DATABASE_URL" in st.secrets:
        os.environ["TURSO_DATABASE_URL"] = st.secrets["TURSO_DATABASE_URL"]
        os.environ["TURSO_AUTH_TOKEN"] = st.secrets["TURSO_AUTH_TOKEN"]
except Exception:
    pass

TURSO_URL = os.getenv("TURSO_DATABASE_URL")
TURSO_TOKEN = os.getenv("TURSO_AUTH_TOKEN")


@st.cache_resource
def _get_shared_connection():
    conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
    except Exception:
        pass
    return conn


def get_connection():
    return _get_shared_connection()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            onboarding_complete INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('good', 'bad')),
            score REAL NOT NULL DEFAULT 50.0,
            relapse_penalty_active INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            done INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
            UNIQUE(category_id, date)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            state TEXT NOT NULL CHECK(state IN ('submitted', 'opened_no_submit', 'penalty_applied')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, date)
        )
    """)

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized: vector_axis.db")
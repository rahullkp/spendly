import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

# spendly.db lives in the project root, next to app.py
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spendly.db")


def get_db():
    """Open a connection with dict-like rows and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables. Safe to call many times."""
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            email         TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at    TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL NOT NULL,
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()
    conn.close()


def seed_db():
    """Insert a demo user and sample expenses, but only on an empty database."""
    conn = get_db()

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] > 0:
        conn.close()
        return

    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123", method="pbkdf2:sha256")),
    )
    user_id = cursor.lastrowid

    today = date.today()
    month_start = today.replace(day=1)

    def day(number):
        return month_start.replace(day=number).isoformat()  # YYYY-MM-DD

    expenses = [
        (user_id, 42.50, "Food", day(1), "Groceries"),
        (user_id, 15.00, "Transport", day(3), "Bus pass top-up"),
        (user_id, 120.00, "Bills", day(5), "Electricity bill"),
        (user_id, 35.75, "Health", day(8), "Pharmacy"),
        (user_id, 18.99, "Entertainment", day(12), "Movie tickets"),
        (user_id, 64.20, "Shopping", day(15), "New shoes"),
        (user_id, 10.00, "Other", day(18), "Donation"),
        (user_id, 27.30, "Food", day(22), "Dinner out"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        expenses,
    )
    conn.commit()
    conn.close()

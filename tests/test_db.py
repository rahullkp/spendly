import re
import sqlite3

import pytest
from werkzeug.security import check_password_hash

from database import db

CATEGORIES = {"Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"}


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    """Point the db module at a throwaway file so spendly.db is never touched."""
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    return db


@pytest.fixture
def seeded_db(fresh_db):
    fresh_db.seed_db()
    return fresh_db


def count(table):
    conn = db.get_db()
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        conn.close()


# ---------------------------- get_db ---------------------------- #

def test_get_db_enables_foreign_keys(fresh_db):
    conn = fresh_db.get_db()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    conn.close()


def test_get_db_returns_dict_like_rows(fresh_db):
    conn = fresh_db.get_db()
    row = conn.execute("SELECT 1 AS one").fetchone()
    assert row["one"] == 1
    conn.close()


# ---------------------------- init_db --------------------------- #

def test_init_db_creates_both_tables(fresh_db):
    conn = fresh_db.get_db()
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"users", "expenses"} <= names


def test_init_db_is_safe_to_repeat(fresh_db):
    fresh_db.init_db()
    fresh_db.init_db()
    assert count("users") == 0


# ---------------------------- seed_db --------------------------- #

def test_seed_creates_demo_user_and_eight_expenses(seeded_db):
    assert count("users") == 1
    assert count("expenses") == 8


def test_seed_does_not_duplicate(seeded_db):
    seeded_db.seed_db()
    seeded_db.seed_db()
    assert count("users") == 1
    assert count("expenses") == 8


def test_seed_demo_user_password_is_hashed(seeded_db):
    conn = seeded_db.get_db()
    user = conn.execute("SELECT * FROM users").fetchone()
    conn.close()
    assert user["email"] == "demo@spendly.com"
    assert user["name"] == "Demo User"
    assert user["password_hash"] != "demo123"
    assert check_password_hash(user["password_hash"], "demo123")


def test_seed_covers_every_category(seeded_db):
    conn = seeded_db.get_db()
    used = {r["category"] for r in conn.execute("SELECT category FROM expenses")}
    conn.close()
    assert used == CATEGORIES


def test_seed_dates_are_iso_and_amounts_are_floats(seeded_db):
    conn = seeded_db.get_db()
    rows = conn.execute("SELECT amount, date FROM expenses").fetchall()
    conn.close()
    for row in rows:
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["date"])
        assert isinstance(row["amount"], float)


def test_seed_expenses_belong_to_demo_user(seeded_db):
    conn = seeded_db.get_db()
    owners = {r["user_id"] for r in conn.execute("SELECT user_id FROM expenses")}
    user_id = conn.execute("SELECT id FROM users").fetchone()["id"]
    conn.close()
    assert owners == {user_id}


# ------------------------- constraints -------------------------- #

def test_duplicate_email_is_rejected(seeded_db):
    conn = seeded_db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Other", "demo@spendly.com", "x"),
        )
    conn.close()


def test_expense_with_unknown_user_is_rejected(fresh_db):
    conn = fresh_db.get_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (999, 1.0, "Food", "2026-10-01"),
        )
    conn.close()

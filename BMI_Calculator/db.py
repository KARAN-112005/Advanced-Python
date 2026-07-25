"""
db.py - SQLite storage for the BMI Calculator (Advanced Tier)
------------------------------------------------------------------
Handles saving and reading BMI records for multiple named users.
Kept separate from the GUI so it can be tested independently, and so
every database call goes through error handling in one place.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bmi_records.db")


class DatabaseError(Exception):
    """Raised when a database read/write fails, so the GUI can show a
    friendly message instead of crashing."""
    pass


def init_db(db_path=DB_PATH):
    """Create the records table if it doesn't already exist."""
    try:
        connection = sqlite3.connect(db_path)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                height_m REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Could not set up the database: {e}")


def save_record(user_name, weight_kg, height_m, bmi, category, recorded_at, db_path=DB_PATH):
    """Insert one BMI record for a named user."""
    try:
        connection = sqlite3.connect(db_path)
        connection.execute(
            """INSERT INTO bmi_records
               (user_name, weight_kg, height_m, bmi, category, recorded_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_name, weight_kg, height_m, bmi, category, recorded_at),
        )
        connection.commit()
        connection.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Could not save the record: {e}")


def get_records(user_name, db_path=DB_PATH):
    """Return all (recorded_at, bmi) pairs for a user, oldest first."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.execute(
            """SELECT recorded_at, bmi FROM bmi_records
               WHERE user_name = ? ORDER BY id ASC""",
            (user_name,),
        )
        rows = cursor.fetchall()
        connection.close()
        return rows
    except sqlite3.Error as e:
        raise DatabaseError(f"Could not read records: {e}")


def get_all_users(db_path=DB_PATH):
    """Return a sorted list of every distinct user name in the database."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.execute(
            "SELECT DISTINCT user_name FROM bmi_records ORDER BY user_name ASC"
        )
        users = [row[0] for row in cursor.fetchall()]
        connection.close()
        return users
    except sqlite3.Error as e:
        raise DatabaseError(f"Could not read the user list: {e}")

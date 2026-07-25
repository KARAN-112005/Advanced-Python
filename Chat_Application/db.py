"""
db.py - SQLite storage for the Chat Application (Advanced Tier)
--------------------------------------------------------------------
Handles three things:
- User accounts (username + hashed password)
- Chat rooms (named, created on demand)
- Messages (tied to a room, with the sender and a timestamp)

Kept separate from app.py so the storage logic can be tested without
running a web server.
"""

import sqlite3
import datetime
import os

from werkzeug.security import generate_password_hash, check_password_hash

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "chat_app.db")


def get_connection(db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DEFAULT_DB_PATH):
    """Create the users, rooms, and messages tables if they don't exist yet."""
    conn = get_connection(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            sent_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------
# Users
# ---------------------------------------------------------------

def create_user(username, password, db_path=DEFAULT_DB_PATH):
    """
    Register a new user with a securely hashed password.
    Raises ValueError if the username is already taken.
    """
    conn = get_connection(db_path)
    try:
        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"Username '{username}' is already taken.")
    finally:
        conn.close()


def verify_user(username, password, db_path=DEFAULT_DB_PATH):
    """Return True if the username exists and the password matches."""
    conn = get_connection(db_path)
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if row is None:
        return False
    return check_password_hash(row["password_hash"], password)


# ---------------------------------------------------------------
# Rooms
# ---------------------------------------------------------------

def get_or_create_room(name, creator, db_path=DEFAULT_DB_PATH):
    """
    Return the room if it already exists (letting a user "join" it),
    or create it if it doesn't ("create" a new room). Either way,
    the room ends up existing.
    """
    conn = get_connection(db_path)
    row = conn.execute("SELECT id FROM rooms WHERE name = ?", (name,)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO rooms (name, created_by) VALUES (?, ?)", (name, creator)
        )
        conn.commit()
    conn.close()


def get_all_rooms(db_path=DEFAULT_DB_PATH):
    """Return a list of all room names, most recently created first."""
    conn = get_connection(db_path)
    rows = conn.execute("SELECT name FROM rooms ORDER BY id DESC").fetchall()
    conn.close()
    return [row["name"] for row in rows]


# ---------------------------------------------------------------
# Messages
# ---------------------------------------------------------------

def save_message(room_name, username, content, db_path=DEFAULT_DB_PATH):
    """Store one chat message, stamped with the current time."""
    conn = get_connection(db_path)
    sent_at = datetime.datetime.now().isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO messages (room_name, username, content, sent_at) VALUES (?, ?, ?, ?)",
        (room_name, username, content, sent_at),
    )
    conn.commit()
    conn.close()
    return sent_at


def get_recent_messages(room_name, limit=50, db_path=DEFAULT_DB_PATH):
    """
    Return the most recent `limit` messages for a room, oldest first,
    as a list of dicts. This is the "message history" loaded when a
    user joins a room.
    """
    conn = get_connection(db_path)
    rows = conn.execute(
        """
        SELECT username, content, sent_at FROM (
            SELECT id, username, content, sent_at FROM messages
            WHERE room_name = ?
            ORDER BY id DESC
            LIMIT ?
        )
        ORDER BY id ASC
        """,
        (room_name, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

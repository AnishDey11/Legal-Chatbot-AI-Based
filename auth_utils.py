import sqlite3
import streamlit as st
import os
import hashlib
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def hash_password(password):
    """Hashes a password using the SHA-256 algorithm."""
    return hashlib.sha256(password.encode()).hexdigest()


# Initialize database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            profile_pic BLOB
        )
    """)
    # Create chat sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_name TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    # Create chat history table linked to sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def add_user(first_name, last_name, email, password, profile_pic=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (first_name, last_name, email, password, profile_pic) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, hashed_password, profile_pic),
        )
        conn.commit()
        st.success("Account created successfully! You are now signed in.")
        return True
    except sqlite3.IntegrityError:
        st.error("Email already registered. Please sign in.")
        return False
    finally:
        conn.close()


def get_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute(
        "SELECT id, first_name, last_name, email, profile_pic FROM users WHERE email=? AND password=?",
        (email, hashed_password),
    )
    result = cursor.fetchone()
    conn.close()
    return result


def is_password_valid(password):
    """
    Checks if the password meets the specified constraints.
    """
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")

    if errors:
        for error in errors:
            st.error(error)
        return False
    return True


def sign_in(email, password):
    user = get_user(email, password)
    if not user:
        st.error("Invalid email or password.")
        return False
    st.session_state["user"] = {
        "id": user[0],
        "first_name": user[1],
        "last_name": user[2],
        "email": user[3],
        "profile_pic": user[4],
    }
    st.success(f"Welcome back, {user[1]}!")
    return True


def sign_up(first_name, last_name, email, password, confirm_password, profile_pic):
    if "@" not in email:
        st.error("Please enter a valid email address.")
        return False
    if password != confirm_password:
        st.error("Passwords do not match.")
        return False

    if not is_password_valid(password):
        return False

    pic_bytes = profile_pic.read() if profile_pic else None
    if add_user(first_name, last_name, email, password, pic_bytes):
        return sign_in(email, password)
    return False


def sign_out():
    keys_to_delete = ["user", "messages", "session_id", "current_session_id"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out successfully.")


def update_user(user_id, first_name, last_name, password=None, profile_pic=None):
    """Updates a user's details in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "UPDATE users SET first_name = ?, last_name = ?"
    params = [first_name, last_name]

    if password:
        if not is_password_valid(password):
            conn.close()
            return None
        hashed_password = hash_password(password)
        query += ", password = ?"
        params.append(hashed_password)

    if profile_pic is not None:
        query += ", profile_pic = ?"
        params.append(profile_pic)

    query += " WHERE id = ?"
    params.append(user_id)

    try:
        cursor.execute(query, tuple(params))
        conn.commit()

        cursor.execute("SELECT id, first_name, last_name, email, profile_pic FROM users WHERE id=?", (user_id,))
        updated_user = cursor.fetchone()
        return updated_user
    except sqlite3.Error as e:
        st.error(f"An error occurred while updating your profile: {e}")
        return None
    finally:
        conn.close()


# --- Functions for chat history and sessions ---

def create_new_session(user_id, session_name):
    """Creates a new chat session and returns its ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_sessions (user_id, session_name) VALUES (?, ?)",
            (user_id, session_name),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        st.error(f"Database error while creating session: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_sessions(user_id):
    """Retrieves all chat sessions for a user."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, session_name FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return cursor.fetchall()
    except sqlite3.Error as e:
        st.error(f"Database error while fetching sessions: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_session(session_id):
    """Deletes a chat session and its associated messages."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error while deleting session: {e}")
    finally:
        if conn:
            conn.close()


def add_message_to_history(session_id, role, content):
    """Adds a chat message to a specific session in the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error while saving message: {e}")
    finally:
        if conn:
            conn.close()


def get_session_history(session_id):
    """Retrieves the chat history for a specific session."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_history WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        )
        history = cursor.fetchall()
        return [{"role": role, "content": content} for role, content in history]
    except sqlite3.Error as e:
        st.error(f"Database error while retrieving history: {e}")
        return []
    finally:
        if conn:
            conn.close()
"""
Authentication utilities for user registration and login.
Uses SQLite for user storage with password hashing.
"""
import sqlite3
import hashlib
from pathlib import Path

# Database configuration
DB_PATH = Path(__file__).resolve().parent / 'permanent_cache' / 'users.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_db_connection():
    """Get SQLite database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """Initialize database with users table if it doesn't exist."""
    conn = _get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.

    Returns (success, message).
    """
    if not username or not email or not password:
        return False, "Vui lòng điền đầy đủ tất cả các trường"

    if len(username) < 6:
        return False, "Tên người dùng phải có ít nhất 6 ký tự"

    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"

    if '@' not in email:
        return False, "Email không hợp lệ"

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        password_hash = _hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        conn.commit()
        conn.close()
        return True, "Đăng ký thành công! Vui lòng đăng nhập"
    except sqlite3.IntegrityError as e:
        msg = str(e)
        if "username" in msg:
            return False, "Tên người dùng đã tồn tại"
        if "email" in msg:
            return False, "Email đã được sử dụng"
        return False, msg
    except Exception as e:
        return False, f"Lỗi đăng ký: {str(e)}"


def login_user(username: str, password: str) -> tuple[bool, str, dict]:
    """
    Authenticate user credentials.

    Returns (success, message, user_data).
    """
    if not username or not password:
        return False, "Vui lòng điền tên người dùng và mật khẩu", {}

    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users "
            "WHERE (username = ? OR email = ?) AND password = ?",
            (username, username, _hash_password(password)),
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            return True, "Đăng nhập thành công", {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
            }
        return False, "Tên người dùng hoặc mật khẩu không chính xác", {}
    except Exception as e:
        return False, f"Lỗi đăng nhập: {str(e)}", {}


def get_user_by_id(user_id: int) -> dict | None:
    """Get user information by ID."""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,),
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
            }
        return None
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None


def user_exists(user_id: int) -> bool:
    """Check if user exists by ID."""
    try:
        conn = _get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception:
        return False


# Initialize database on module import
init_db()


import sqlite3

DB_NAME = "users.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Add role column if it doesn't exist (for existing databases)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'student';")
    except sqlite3.OperationalError:
        pass  # Column already exists

    conn.commit()
    conn.close()


def create_user(name, email, mobile, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, email, mobile, password, role)
        VALUES (?, ?, ?, ?, ?)
    """, (name, email, mobile, password, role))

    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_email_and_password(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE email = ? AND password = ?
    """, (email, password))

    user = cursor.fetchone()
    conn.close()
    return user


# ✅ Get all users
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, mobile, role FROM users
    """)

    users = cursor.fetchall()
    conn.close()
    return users


# ✅ Update user role
def update_user_role(email, new_role):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET role = ?
        WHERE email = ?
    """, (new_role, email))

    conn.commit()
    conn.close()


def delete_user(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM users WHERE email = ?
    """, (email,))

    conn.commit()
    conn.close()
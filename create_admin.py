#!/usr/bin/env python3

import getpass
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash
import db

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength. Returns (is_valid, error_message)"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*)."
    return True, ""


def validate_mobile(mobile: str) -> tuple[bool, str]:
    """Validate mobile number. Returns (is_valid, error_message)"""
    if not mobile:
        return True, ""  # Mobile is optional
    mobile = mobile.replace(" ", "").replace("-", "")
    if not mobile.isdigit():
        return False, "Mobile number must contain only digits."
    if len(mobile) < 10:
        return False, "Mobile number must be at least 10 digits long."
    if len(mobile) > 15:
        return False, "Mobile number must not exceed 15 digits."
    return True, ""


def update_password(email: str, hashed_password: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, email))
    conn.commit()
    conn.close()


def main():
    print('Create or promote an admin user')

    # Interactive prompts
    name = input('Full name (leave blank for "Admin"): ').strip()
    
    while True:
        email = input('Email (required): ').strip()
        if not email:
            print('Email is required.')
            continue
        if not validate_email(email):
            print('Invalid email format. Please enter a valid email address.')
            continue
        break

    mobile = input('Mobile (optional): ').strip()
    
    if mobile:
        while True:
            is_valid, error_msg = validate_mobile(mobile)
            if not is_valid:
                print(error_msg)
                mobile = input('Mobile (optional): ').strip()
                if not mobile:
                    break
            else:
                break

    while True:
        password = getpass.getpass('Password (required): ').strip()
        if not password:
            print('Password is required.')
            continue
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            print(error_msg)
            continue
        password_confirm = getpass.getpass('Confirm password: ').strip()
        if password != password_confirm:
            print('Passwords do not match. Try again.')
            continue
        break

    # Ensure DB initialized
    db.init_db()

    existing = db.get_user_by_email(email)

    hashed = generate_password_hash(password)

    try:
        if existing:
            # Promote to admin and update password
            db.update_user_role(email, 'admin')
            update_password(email, hashed)
            print(f"Updated existing user '{email}' to role 'admin' and updated password.")
        else:
            name_val = name or 'Admin'
            mobile_val = mobile or ''
            db.create_user(name_val, email, mobile_val, hashed, 'admin')
            print(f"Created admin user '{email}'.")
    except sqlite3.IntegrityError as e:
        print('Database error:', e)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Interactive script to create or promote a user to admin in the SQLite users.db.

Usage:
  python create_admin.py

The script will prompt for name, email, mobile and password.
If a user with the email exists, the script will promote them to role 'admin' and update their password.
"""
import getpass
import sqlite3
import os
from werkzeug.security import generate_password_hash
import db

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')


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
        if email:
            break
        print('Email is required.')

    mobile = input('Mobile (optional): ').strip()

    while True:
        password = getpass.getpass('Password (required): ').strip()
        if not password:
            print('Password is required.')
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

"""
reset_password.py — Quick admin utility to reset a SafeNet Kids user password.
Run: python reset_password.py
"""
import sys
import os
import hashlib
import secrets
import json

USERS_FILE = os.path.join("data", "users.json")

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def main():
    print("\n=== SafeNet Kids — Password Reset Utility ===\n")
    
    if not os.path.exists(USERS_FILE):
        print("ERROR: data/users.json not found. Make sure you run this from the project folder.")
        return

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if not users:
        print("No users found in the database.")
        return

    print("Registered users:", list(users.keys()))
    username = input("\nEnter username to reset: ").strip().lower()
    
    if username not in users:
        print(f"ERROR: User '{username}' not found.")
        return

    new_password = input("Enter new login password: ").strip()
    if len(new_password) < 4:
        print("ERROR: Password must be at least 4 characters.")
        return

    new_parent_password = input("Enter new parent/admin password (or press Enter to keep unchanged): ").strip()

    # Update login password
    salt = secrets.token_hex(16)
    users[username]["salt"] = salt
    users[username]["hashed_password"] = hash_password(new_password, salt)

    # Update parent password if provided
    if new_parent_password:
        if len(new_parent_password) < 4:
            print("ERROR: Parent password must be at least 4 characters.")
            return
        parent_salt = secrets.token_hex(16)
        users[username]["parent_salt"] = parent_salt
        users[username]["parent_hashed_password"] = hash_password(new_parent_password, parent_salt)
        print(f"\n[OK] Login password AND parent password reset for '{username}'.")
    else:
        print(f"\n[OK] Login password reset for '{username}'. Parent password unchanged.")

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

    print("You can now sign in at http://localhost:5000 with the new password.\n")

if __name__ == "__main__":
    main()

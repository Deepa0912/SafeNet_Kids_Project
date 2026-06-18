import hashlib
import json
import os
import secrets


USERS_FILE = os.path.join("data", "users.json")


class AuthManager:
    """Manages user accounts stored in data/users.json.
    Passwords are hashed with sha256 + random salt (no extra dependencies).
    Each account has a separate parent/admin password used by the AuthWindow gate.
    """

    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(USERS_FILE):
            with open(USERS_FILE, "w") as f:
                json.dump({}, f)
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self):
        with open(USERS_FILE, "r") as f:
            self._users: dict = json.load(f)

    def _save(self):
        with open(USERS_FILE, "w") as f:
            json.dump(self._users, f, indent=2)

    @staticmethod
    def _hash(password: str, salt: str) -> str:
        return hashlib.sha256((salt + password).encode()).hexdigest()

    @staticmethod
    def _new_salt() -> str:
        return secrets.token_hex(16)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def username_exists(self, username: str) -> bool:
        self._load()
        return username.strip().lower() in self._users

    def register(self, username: str, password: str, parent_password: str) -> tuple[bool, str]:
        """Register a new account.
        Returns (success, error_message).  error_message is '' on success.
        """
        username = username.strip()
        if not username:
            return False, "Username cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        if len(parent_password) < 4:
            return False, "Parent password must be at least 4 characters."

        self._load()
        key = username.lower()
        if key in self._users:
            return False, f"Username '{username}' is already taken."

        salt = self._new_salt()
        parent_salt = self._new_salt()
        self._users[key] = {
            "username": username,               # original casing for display
            "salt": salt,
            "hashed_password": self._hash(password, salt),
            "parent_salt": parent_salt,
            "parent_hashed_password": self._hash(parent_password, parent_salt),
        }
        self._save()
        return True, ""

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Validate login credentials.
        Returns (success, error_message).
        """
        self._load()
        key = username.strip().lower()
        if key not in self._users:
            return False, "Username not found."
        user = self._users[key]
        if self._hash(password, user["salt"]) != user["hashed_password"]:
            return False, "Incorrect password."
        return True, ""

    def verify_parent_password(self, username: str, parent_password: str) -> bool:
        """Check the parent/admin password for a given user."""
        self._load()
        key = username.strip().lower()
        if key not in self._users:
            return False
        user = self._users[key]
        return self._hash(parent_password, user["parent_salt"]) == user["parent_hashed_password"]

    def get_display_name(self, username: str) -> str:
        """Return the original-casing display name."""
        self._load()
        key = username.strip().lower()
        if key in self._users:
            return self._users[key].get("username", username)
        return username

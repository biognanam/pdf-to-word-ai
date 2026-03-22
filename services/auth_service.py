"""Authentication service for local username/password login."""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AuthIdentity:
    """Authenticated user identity."""

    username: str
    role: str


class AuthService:
    """Simple environment-driven auth provider."""

    def __init__(self, auth_users_config: str, logger) -> None:
        self.logger = logger
        self.users = self._parse_users(auth_users_config)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _parse_users(self, auth_users_config: str) -> Dict[str, Dict[str, str]]:
        users: Dict[str, Dict[str, str]] = {}
        entries = [segment.strip() for segment in auth_users_config.split(",") if segment.strip()]

        for entry in entries:
            parts = [part.strip() for part in entry.split("|")]
            if len(parts) < 2:
                continue
            username = parts[0].lower()
            password = parts[1]
            role = parts[2] if len(parts) >= 3 else "User"
            users[username] = {
                "username": parts[0],
                "password_hash": self._hash_password(password),
                "role": role,
            }

        self.logger.info("Auth users loaded: %s", ", ".join(sorted(users.keys())))
        return users

    def authenticate(self, username: str, password: str) -> Optional[AuthIdentity]:
        """Validate credentials and return identity on success."""
        if not username or not password:
            return None

        user_record = self.users.get(username.strip().lower())
        if not user_record:
            return None

        incoming_hash = self._hash_password(password)
        if not hmac.compare_digest(incoming_hash, user_record["password_hash"]):
            return None

        self.logger.info("User authenticated: %s", user_record["username"])
        return AuthIdentity(username=user_record["username"], role=user_record["role"])

    def list_usernames(self) -> list[str]:
        """Return configured usernames."""
        return sorted(record["username"] for record in self.users.values())

"""Temporary role-based mock accounts and in-memory sessions for SaigonBite."""
import hmac
import os
import secrets
import threading
import time

SESSION_COOKIE = "saigonbite_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
ROLE_HOME = {
    "CUSTOMER": "/customer/",
    "KITCHEN_STAFF": "/kitchen/",
    "ADMIN": "/admin/",
}
MOCK_ACCOUNTS = (
    {
        "email": os.getenv("SAIGONBITE_CUSTOMER_EMAIL", "customer@saigonbite.com").strip().lower(),
        "password": os.getenv("SAIGONBITE_CUSTOMER_PASSWORD", "password123"),
        "role": "CUSTOMER",
    },
    {
        "email": os.getenv("SAIGONBITE_DEMO_EMAIL", "kitchen@saigonbite.com").strip().lower(),
        "password": os.getenv("SAIGONBITE_DEMO_PASSWORD", "password123"),
        "role": "KITCHEN_STAFF",
    },
    {
        "email": os.getenv("SAIGONBITE_ADMIN_EMAIL", "admin@saigonbite.com").strip().lower(),
        "password": os.getenv("SAIGONBITE_ADMIN_PASSWORD", "password123"),
        "role": "ADMIN",
    },
)
DEMO_EMAIL = MOCK_ACCOUNTS[1]["email"]
DEMO_PASSWORD = MOCK_ACCOUNTS[1]["password"]

_sessions: dict[str, dict] = {}
_sessions_lock = threading.Lock()


def create_session(email: str, role: str, *, demo: bool) -> str:
    token = secrets.token_urlsafe(32)
    now = time.time()
    with _sessions_lock:
        expired = [key for key, value in _sessions.items() if now - value["created_at"] >= SESSION_TTL_SECONDS]
        for key in expired:
            _sessions.pop(key, None)
        _sessions[token] = {"email": email, "role": role, "demo": demo, "created_at": now}
    return token


def get_session(token: str | None) -> dict | None:
    if not token:
        return None
    with _sessions_lock:
        session = _sessions.get(token)
        if session and time.time() - session["created_at"] < SESSION_TTL_SECONDS:
            return session.copy()
        _sessions.pop(token, None)
        return None


def clear_session(token: str | None) -> None:
    if token:
        with _sessions_lock:
            _sessions.pop(token, None)


def authenticate_credentials(email: str, password: str) -> dict | None:
    normalized_email = email.strip().lower()
    email_bytes = normalized_email.encode("utf-8")
    password_bytes = password.encode("utf-8")
    for account in MOCK_ACCOUNTS:
        email_match = hmac.compare_digest(email_bytes, account["email"].encode("utf-8"))
        password_match = hmac.compare_digest(password_bytes, account["password"].encode("utf-8"))
        if email_match and password_match:
            return {"email": account["email"], "role": account["role"]}
    return None


def role_home(role: str) -> str:
    return ROLE_HOME.get(role, "/")

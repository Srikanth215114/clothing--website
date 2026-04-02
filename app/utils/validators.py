import re


USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


def require_fields(payload: dict, fields: list[str]):
    missing = [f for f in fields if not payload.get(f)]
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(missing)}")


def validate_username(username: str):
    if not USERNAME_RE.match(username or ""):
        raise ValueError("Username must be 3-32 chars and contain only letters, numbers, underscore.")


def validate_email(email: str):
    email = (email or "").strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Invalid email address.")


def validate_password(password: str):
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")


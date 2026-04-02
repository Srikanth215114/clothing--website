from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models.user import User
from ..utils.security import hash_password, verify_password
from ..utils.validators import (
    require_fields,
    validate_email,
    validate_password,
    validate_username,
)


def register_user(payload: dict) -> dict:
    require_fields(payload, ["username", "email", "password"])
    username = payload["username"].strip()
    email = payload["email"].strip().lower()
    password = payload["password"]

    validate_username(username)
    validate_email(email)
    validate_password(password)

    if User.query.filter_by(username=username).first():
        raise ValueError("Username already exists.")
    if User.query.filter_by(email=email).first():
        raise ValueError("Email already exists.")

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.session.add(user)
    db.session.commit()
    token = create_access_token(
        identity=str(user.id), additional_claims={"is_admin": user.is_admin}
    )
    return {"access_token": token, "user": user.to_public_dict()}


def login(payload: dict, enable_session: bool = True) -> dict:
    require_fields(payload, ["username", "password"])
    username = payload["username"].strip()
    password = payload["password"]

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid username or password.")

    if enable_session:
        login_user(user)

    token = create_access_token(identity=str(user.id), additional_claims={"is_admin": user.is_admin})
    return {"access_token": token, "user": user.to_public_dict()}


def logout(enable_session: bool = True):
    if enable_session:
        logout_user()


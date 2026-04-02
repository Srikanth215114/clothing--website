from flask import Blueprint, request

from ..services.auth_service import login, logout, register_user
from ._helpers import fail, ok

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    try:
        payload = request.get_json(silent=True) or {}
        result = register_user(payload)
        return ok(result, 201)
    except ValueError as e:
        return fail(str(e), 400)


@auth_bp.post("/login")
def do_login():
    try:
        payload = request.get_json(silent=True) or {}
        enable_session = bool(payload.get("enable_session", True))
        result = login(payload, enable_session=enable_session)
        return ok(result, 200)
    except ValueError as e:
        return fail(str(e), 401)


@auth_bp.post("/logout")
def do_logout():
    logout(enable_session=True)
    return ok({"message": "Logged out."})


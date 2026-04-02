from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models.user import User
from ..services.cart_service import add_to_cart, get_or_create_cart, remove_cart_item, update_cart_item
from ._helpers import fail, ok

cart_bp = Blueprint("cart", __name__)


def _current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return db.session.get(User, int(user_id))


@cart_bp.get("")
@jwt_required()
def view_cart():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)
    cart = get_or_create_cart(user)
    return ok(cart.to_dict())


@cart_bp.post("/add")
@jwt_required()
def add_item():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)

    payload = request.get_json(silent=True) or {}
    try:
        if payload.get("product_id") is None:
            return fail("product_id is required.", 400)
        cart = add_to_cart(
            user=user,
            product_id=int(payload["product_id"]),
            quantity=int(payload.get("quantity") or 1),
            size=(payload.get("size") or None),
        )
        return ok(cart.to_dict(), 201)
    except (TypeError, ValueError) as e:
        return fail(str(e), 400)


@cart_bp.put("/update")
@jwt_required()
def update_item():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)

    payload = request.get_json(silent=True) or {}
    try:
        if payload.get("item_id") is None or payload.get("quantity") is None:
            return fail("item_id and quantity are required.", 400)
        cart = update_cart_item(
            user=user,
            item_id=int(payload["item_id"]),
            quantity=int(payload["quantity"]),
        )
        return ok(cart.to_dict(), 200)
    except (TypeError, ValueError) as e:
        return fail(str(e), 400)


@cart_bp.delete("/remove")
@jwt_required()
def remove_item():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)

    payload = request.get_json(silent=True) or {}
    raw_id = payload.get("item_id") if payload else None
    if raw_id is None:
        raw_id = request.args.get("item_id", type=int)
    if raw_id is None:
        return fail("item_id is required.", 400)
    try:
        cart = remove_cart_item(user=user, item_id=int(raw_id))
        return ok(cart.to_dict(), 200)
    except (TypeError, ValueError) as e:
        return fail(str(e), 400)


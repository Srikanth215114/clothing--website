from flask import Blueprint, request
from flask_jwt_extended import get_jwt, jwt_required

from ..models.order import Order
from ..services.product_service import create_product, delete_product, get_product, update_product
from ._helpers import fail, ok

admin_bp = Blueprint("admin", __name__)


def _require_admin():
    claims = get_jwt() or {}
    return bool(claims.get("is_admin"))


@admin_bp.post("/products")
@jwt_required()
def admin_create_product():
    if not _require_admin():
        return fail("Forbidden.", 403)
    try:
        payload = request.get_json(silent=True) or {}
        product = create_product(payload)
        return ok(product.to_dict(), 201)
    except ValueError as e:
        return fail(str(e), 400)


@admin_bp.put("/products/<int:product_id>")
@jwt_required()
def admin_update_product(product_id: int):
    if not _require_admin():
        return fail("Forbidden.", 403)
    product = get_product(product_id)
    if not product:
        return fail("Product not found.", 404)
    try:
        payload = request.get_json(silent=True) or {}
        product = update_product(product, payload)
        return ok(product.to_dict(), 200)
    except ValueError as e:
        return fail(str(e), 400)


@admin_bp.delete("/products/<int:product_id>")
@jwt_required()
def admin_delete_product(product_id: int):
    if not _require_admin():
        return fail("Forbidden.", 403)
    product = get_product(product_id)
    if not product:
        return fail("Product not found.", 404)
    delete_product(product)
    return ok({"deleted": True})


@admin_bp.get("/orders")
@jwt_required()
def admin_list_orders():
    if not _require_admin():
        return fail("Forbidden.", 403)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return ok([o.to_dict() for o in orders])


from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import db
from ..models.user import User
from ..models.order import Order, OrderItem
from ..services.cart_service import clear_cart, get_or_create_cart
from ._helpers import fail, ok

order_bp = Blueprint("orders", __name__)


def _current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return db.session.get(User, int(user_id))


@order_bp.post("/create")
@jwt_required()
def create_order():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)

    cart = get_or_create_cart(user)
    if not cart.items:
        return fail("Cart is empty.", 400)

    payload = request.get_json(silent=True) or {}
    try:
        shipping_cents = int(payload.get("shipping_cents", 0) or 0)
    except (TypeError, ValueError):
        return fail("Invalid shipping_cents.", 400)
    if shipping_cents < 0:
        return fail("Invalid shipping_cents.", 400)

    subtotal_cents = sum(i.unit_price_cents * i.quantity for i in cart.items)
    total_cents = subtotal_cents + shipping_cents

    # Validate stock before writing order (avoid partial commits)
    for item in list(cart.items):
        product = item.product
        if not product:
            return fail("Cart contains invalid items.", 400)
        if product.stock_qty < item.quantity:
            return fail(f"Insufficient stock for {product.name}.", 400)

    try:
        order = Order(
            user_id=user.id,
            status="created",
            subtotal_cents=subtotal_cents,
            shipping_cents=shipping_cents,
            total_cents=total_cents,
        )
        db.session.add(order)
        db.session.flush()

        for item in list(cart.items):
            product = item.product
            product.stock_qty -= item.quantity
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    size=item.size,
                    quantity=item.quantity,
                    unit_price_cents=item.unit_price_cents,
                )
            )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    oid = order.id
    clear_cart(user)
    # New commit in clear_cart may expire instances; reload for response
    order_row = db.session.get(Order, oid)
    if not order_row:
        return fail("Order could not be loaded.", 500)
    return ok(order_row.to_dict(), 201)


@order_bp.get("")
@jwt_required()
def list_orders():
    user = _current_user()
    if not user:
        return fail("Unauthorized.", 401)

    orders = (
        Order.query.filter_by(user_id=user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return ok([o.to_dict() for o in orders])

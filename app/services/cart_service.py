from ..extensions import db
from ..models.cart import Cart, CartItem
from ..models.product import Product
from ..models.user import User


def _norm_size(size: str | None) -> str:
    s = (size or "").strip()
    return s if s else "M"


def get_or_create_cart(user: User) -> Cart:
    if user.cart:
        return user.cart
    cart = Cart(user_id=user.id)
    db.session.add(cart)
    db.session.commit()
    return cart


def add_to_cart(user: User, product_id: int, quantity: int, size: str | None = None) -> Cart:
    product = db.session.get(Product, product_id)
    if not product:
        raise ValueError("Product not found.")
    if product.stock_qty <= 0:
        raise ValueError("Product is out of stock.")

    qty = int(quantity or 1)
    if qty <= 0:
        raise ValueError("Quantity must be > 0.")

    cart = get_or_create_cart(user)
    sz = _norm_size(size)

    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id, size=sz).first()
    if item:
        if item.quantity + qty > product.stock_qty:
            raise ValueError("Not enough stock for this product.")
        item.quantity += qty
    else:
        if qty > product.stock_qty:
            raise ValueError("Not enough stock for this product.")
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            size=sz,
            quantity=qty,
            unit_price_cents=product.price_cents,
        )
        db.session.add(item)

    db.session.commit()
    return cart


def update_cart_item(user: User, item_id: int, quantity: int) -> Cart:
    cart = get_or_create_cart(user)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise ValueError("Cart item not found.")

    qty = int(quantity or 0)
    if qty <= 0:
        db.session.delete(item)
    else:
        product = item.product
        if product and qty > product.stock_qty:
            raise ValueError("Not enough stock for this product.")
        item.quantity = qty

    db.session.commit()
    return cart


def remove_cart_item(user: User, item_id: int) -> Cart:
    cart = get_or_create_cart(user)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        raise ValueError("Cart item not found.")
    db.session.delete(item)
    db.session.commit()
    return cart


def clear_cart(user: User):
    cart = get_or_create_cart(user)
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()


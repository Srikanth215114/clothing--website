from datetime import datetime

from ..extensions import db


class Cart(db.Model):
    __tablename__ = "carts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = db.relationship("User", back_populates="cart")
    items = db.relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def totals(self):
        subtotal_cents = sum(item.unit_price_cents * item.quantity for item in self.items)
        return {"subtotal_cents": subtotal_cents}

    def to_dict(self):
        totals = self.totals()
        return {
            "id": self.id,
            "items": [item.to_dict() for item in self.items],
            **totals,
        }


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)

    # Non-null avoids SQLite UNIQUE quirks with NULL; normalized in cart_service (e.g. "M").
    size = db.Column(db.String(30), nullable=False, default="", server_default="")
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price_cents = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    cart = db.relationship("Cart", back_populates="items")
    product = db.relationship("Product")

    __table_args__ = (
        db.UniqueConstraint("cart_id", "product_id", "size", name="uq_cart_product_size"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "product": self.product.to_dict() if self.product else None,
            "product_id": self.product_id,
            "size": self.size,
            "quantity": self.quantity,
            "unit_price_cents": self.unit_price_cents,
            "line_total_cents": self.unit_price_cents * self.quantity,
        }


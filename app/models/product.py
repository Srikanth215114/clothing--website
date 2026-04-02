from datetime import datetime

from ..extensions import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    products = db.relationship("Product", back_populates="category", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    price_cents = db.Column(db.Integer, nullable=False)
    stock_qty = db.Column(db.Integer, nullable=False, default=0)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    category = db.relationship("Category", back_populates="products")

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "image_url": self.image_url,
            "price_cents": self.price_cents,
            "price": self.price_cents / 100.0,
            "stock_qty": self.stock_qty,
            "category": self.category.to_dict() if self.category else None,
        }


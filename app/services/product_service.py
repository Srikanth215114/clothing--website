from ..extensions import db
from ..models.product import Category, Product


def list_products(category: str | None = None):
    q = Product.query
    if category:
        q = q.join(Category).filter(Category.name.ilike(category))
    return q.order_by(Product.id.asc()).all()


def get_product(product_id: int) -> Product | None:
    return db.session.get(Product, product_id)


def get_or_create_category(name: str) -> Category:
    name = (name or "").strip()
    if not name:
        raise ValueError("Category name is required.")
    existing = Category.query.filter(Category.name.ilike(name)).first()
    if existing:
        return existing
    cat = Category(name=name)
    db.session.add(cat)
    db.session.flush()
    return cat


def create_product(payload: dict) -> Product:
    name = (payload.get("name") or "").strip()
    if not name:
        raise ValueError("Product name is required.")

    category = get_or_create_category(payload.get("category", "Uncategorized"))
    price_cents = int(payload.get("price_cents") or 0)
    stock_qty = int(payload.get("stock_qty") or 0)
    if price_cents <= 0:
        raise ValueError("price_cents must be > 0.")
    if stock_qty < 0:
        raise ValueError("stock_qty must be >= 0.")

    product = Product(
        name=name,
        description=(payload.get("description") or "").strip() or None,
        image_url=(payload.get("image_url") or "").strip() or None,
        price_cents=price_cents,
        stock_qty=stock_qty,
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return product


def update_product(product: Product, payload: dict) -> Product:
    if "name" in payload:
        name = (payload.get("name") or "").strip()
        if not name:
            raise ValueError("Product name cannot be empty.")
        product.name = name

    if "description" in payload:
        product.description = (payload.get("description") or "").strip() or None

    if "image_url" in payload:
        product.image_url = (payload.get("image_url") or "").strip() or None

    if "price_cents" in payload:
        price_cents = int(payload.get("price_cents") or 0)
        if price_cents <= 0:
            raise ValueError("price_cents must be > 0.")
        product.price_cents = price_cents

    if "stock_qty" in payload:
        stock_qty = int(payload.get("stock_qty") or 0)
        if stock_qty < 0:
            raise ValueError("stock_qty must be >= 0.")
        product.stock_qty = stock_qty

    if "category" in payload:
        product.category = get_or_create_category(payload.get("category"))

    db.session.commit()
    return product


def delete_product(product: Product):
    db.session.delete(product)
    db.session.commit()


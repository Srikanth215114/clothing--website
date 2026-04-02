from flask import Blueprint

from ..services.product_service import get_product, list_products
from ._helpers import fail, ok

product_bp = Blueprint("products", __name__)


@product_bp.get("")
def products_index():
    products = list_products()
    return ok([p.to_dict() for p in products])


@product_bp.get("/<int:product_id>")
def product_detail(product_id: int):
    product = get_product(product_id)
    if not product:
        return fail("Product not found.", 404)
    return ok(product.to_dict())


@product_bp.get("/category/<string:category>")
def products_by_category(category: str):
    products = list_products(category=category)
    return ok([p.to_dict() for p in products])


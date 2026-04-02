import os
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

from config import DevelopmentConfig, ProductionConfig

from .extensions import bcrypt, cors, db, jwt, login_manager, migrate


def create_app():
    app = Flask(
        __name__,
        static_folder=None,
    )

    # Flask 3: use FLASK_ENV instead of removed app.env
    flask_env = os.environ.get("FLASK_ENV", "development").lower()
    if flask_env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Absolute path to existing static HTML/CSS under project root /files
    project_root = Path(__file__).resolve().parent.parent
    app.config["FRONTEND_ROOT"] = str(project_root / "files")

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = None  # API + JWT; no redirect to login page

    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # JWT-friendly JSON errors (instead of HTML)
    @jwt.expired_token_loader
    def _expired_token(_jwt_header, _jwt_payload):
        return jsonify({"ok": False, "error": {"message": "Token has expired", "code": "TOKEN_EXPIRED"}}), 401

    @jwt.invalid_token_loader
    def _invalid_token(err: str):
        return jsonify({"ok": False, "error": {"message": err or "Invalid token", "code": "INVALID_TOKEN"}}), 401

    @jwt.unauthorized_loader
    def _missing_token(err: str):
        return jsonify({"ok": False, "error": {"message": err or "Authorization required", "code": "UNAUTHORIZED"}}), 401

    # Models import for migrations
    from .models.user import User  # noqa: F401
    from .models.product import Category, Product  # noqa: F401
    from .models.cart import Cart, CartItem  # noqa: F401
    from .models.order import Order, OrderItem  # noqa: F401

    # Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.cart_routes import cart_bp
    from .routes.order_routes import order_bp
    from .routes.product_routes import product_bp
    from .routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(product_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(order_bp, url_prefix="/api/orders")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    with app.app_context():
        db.create_all()

    root = app.config["FRONTEND_ROOT"]

    @app.get("/")
    def serve_index():
        return send_from_directory(root, "index.html")

    @app.get("/<path:path>")
    def serve_frontend(path: str):
        # Do not treat unknown API paths as static files
        if path.startswith("api/"):
            abort(404)
        try:
            return send_from_directory(root, path)
        except FileNotFoundError:
            abort(404)

    return app

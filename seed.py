import os

from app import create_app
from app.extensions import db
from app.models.product import Category, Product
from app.models.user import User
from app.utils.security import hash_password


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if Product.query.count() == 0:
            anime = Category(name="Anime Streetwear")
            db.session.add(anime)
            db.session.flush()

            products = [
                ("satoru gojo", "./images/products/product-1.webp"),
                ("monkey d luffy", "./images/products/product-2.webp"),
                ("vegeta ultra ego", "./images/products/product-3.webp"),
                ("naruto uzumaki", "./images/products/product-4.webp"),
                ("kakashi hatake", "./images/products/product-5.webp"),
                ("gojo satoru", "./images/products/product-6.webp"),
                ("kakarot", "./images/products/product-7.webp"),
                ("son goku", "./images/products/product-8.webp"),
                ("master roshi", "./images/products/product-9.webp"),
                ("itachi uchiha", "./images/products/product-10.webp"),
                ("meliodas", "./images/products/product-11.webp"),
                ("vegeta", "./images/products/product-12.webp"),
                ("sukuna", "./images/products/product-13.webp"),
                ("zenitsu", "./images/products/product-14.webp"),
                ("sung jin woo", "./images/products/product-15.webp"),
                ("satoru gojo black", "./images/products/product-16.webp"),
            ]

            for name, img in products:
                db.session.add(
                    Product(
                        name=name,
                        description=f"Premium anime streetwear tee: {name}.",
                        image_url=img,
                        price_cents=79900,
                        stock_qty=25,
                        category_id=anime.id,
                    )
                )

            db.session.commit()
            print("Seeded products.")
        else:
            print("Products already exist; skipping product seed.")

        if not User.query.filter_by(username="admin").first():
            admin_pw = os.environ.get("ADMIN_PASSWORD", "Admin12345!")
            admin = User(
                username="admin",
                email="admin@litup.local",
                password_hash=hash_password(admin_pw),
                is_admin=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("Created admin user (username: admin). Set ADMIN_PASSWORD in production.")
        else:
            print("Admin user already exists; skipping admin seed.")


if __name__ == "__main__":
    seed()

class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_contains_products(self, client, app):
        from backend.seed import run_seed
        with app.app_context():
            run_seed()
        resp = client.get("/")
        assert b"product-card" in resp.data


class TestAboutPage:
    def test_about_returns_200(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_about_has_content(self, client):
        resp = client.get("/about")
        assert "PivdenShop".encode() in resp.data


class TestProductsPage:
    def test_products_page_returns_200(self, client):
        resp = client.get("/products")
        assert resp.status_code == 200

    def test_products_page_shows_grid(self, client, app):
        from backend.seed import run_seed
        with app.app_context():
            run_seed()
        resp = client.get("/products")
        assert b"products-grid" in resp.data


class TestRegisterPage:
    def test_register_page_returns_200(self, client):
        resp = client.get("/register")
        assert resp.status_code == 200

    def test_register_page_has_form(self, client):
        resp = client.get("/register")
        assert b"<form" in resp.data
        assert b"email" in resp.data
        assert b"password" in resp.data
        assert b"phone" in resp.data


class TestProductModal:
    def _seed_product(self, app):
        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (email, phone, password_hash, full_name, is_seller) "
                "VALUES ('seller@test.com', '0501111111', 'hash', 'Оксана Коваль', true) "
                "RETURNING id"
            )
            seller_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (id, seller_id, title, description, price, category) "
                "VALUES (1, %s, 'Тестовий товар', 'Опис товару', 999, 'Електроніка') "
                "ON CONFLICT DO NOTHING",
                (seller_id,),
            )
            cur.close()
            return seller_id

    def test_product_modal_api_returns_200(self, client, app):
        self._seed_product(app)
        resp = client.get("/api/products/1")
        assert resp.status_code == 200
        import json
        data = json.loads(resp.data)
        product = data["product"]
        assert "title" in product
        assert "price" in product
        assert "description" in product
        assert "seller" in product
        assert "reviews" in product

    def test_product_modal_api_invalid_id(self, client, app):
        resp = client.get("/api/products/99999")
        assert resp.status_code == 404

    def test_product_review_submit(self, client, app):
        seller_id = self._seed_product(app)
        import json
        with app.app_context():
            from backend.app.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (email, phone, password_hash, full_name) "
                "VALUES ('buyer@test.com', '0502222222', 'hash', 'Покупець') "
                "RETURNING id"
            )
            buyer_id = cur.fetchone()[0]
            cur.close()

        resp = client.post("/register", json={
            "email": "reviewer@test.com",
            "phone": "0503333333",
            "password": "password123",
        })
        token = json.loads(resp.data)["token"]

        resp = client.post(
            "/api/products/1/reviews",
            json={"text": "Чудовий товар!", "rating": 5},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201


class TestLoginPage:
    def test_login_page_returns_200(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200

    def test_login_page_has_form(self, client):
        resp = client.get("/login")
        assert b"<form" in resp.data
        assert b"email" in resp.data
        assert b"password" in resp.data

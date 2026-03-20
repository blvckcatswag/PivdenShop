import json


class TestCart:
    def _register(self, client, email="cart@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _seed_product(self, app):
        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (email, phone, password_hash, full_name, is_seller) "
                "VALUES ('seller@cart.com', '0509999999', 'hash', 'Продавець', true) "
                "RETURNING id"
            )
            seller_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (seller_id, title, price, category) "
                "VALUES (%s, 'Тестовий товар', 500, 'Електроніка') RETURNING id",
                (seller_id,),
            )
            product_id = cur.fetchone()[0]
            cur.close()
            return product_id

    def test_cart_add_item(self, client, app):
        token = self._register(client)
        product_id = self._seed_product(app)
        resp = client.post("/api/cart", json={
            "product_id": product_id,
            "quantity": 1,
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 201

    def test_cart_get_items(self, client, app):
        token = self._register(client)
        product_id = self._seed_product(app)
        client.post("/api/cart", json={
            "product_id": product_id,
            "quantity": 2,
        }, headers={"Authorization": f"Bearer {token}"})

        resp = client.get("/api/cart", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["total"] == 1000

    def test_cart_remove_item(self, client, app):
        token = self._register(client)
        product_id = self._seed_product(app)
        resp = client.post("/api/cart", json={
            "product_id": product_id,
            "quantity": 1,
        }, headers={"Authorization": f"Bearer {token}"})
        item_id = json.loads(resp.data)["item_id"]

        resp = client.delete(f"/api/cart/{item_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

        resp = client.get("/api/cart", headers={"Authorization": f"Bearer {token}"})
        data = json.loads(resp.data)
        assert len(data["items"]) == 0

    def test_cart_page_returns_200(self, client):
        token = self._register(client)
        resp = client.get("/cart", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_checkout_page_returns_200(self, client):
        token = self._register(client)
        resp = client.get("/checkout", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

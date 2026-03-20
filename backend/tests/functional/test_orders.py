import json


class TestOrdersPage:
    def _register(self, client, email, phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _seed_order(self, app, buyer_id, seller_id, product_id):
        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO products (id, seller_id, title, price) "
                "VALUES (%s, %s, 'Test', 100) ON CONFLICT DO NOTHING",
                (product_id, seller_id),
            )
            cur.execute(
                "INSERT INTO orders (buyer_id, seller_id, product_id, address, card_last4, card_number_plain) "
                "VALUES (%s, %s, %s, 'Kyiv', '4242', '4242424242424242') RETURNING id",
                (buyer_id, seller_id, product_id),
            )
            order_id = cur.fetchone()[0]
            cur.close()
            return order_id

    def test_order_returns_200(self, client, app):
        token = self._register(client, "buyer@test.com")
        seller_token = self._register(client, "seller@test.com", "0507654321")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email = 'buyer@test.com'")
            buyer_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM users WHERE email = 'seller@test.com'")
            seller_id = cur.fetchone()[0]
            cur.close()

        order_id = self._seed_order(app, buyer_id, seller_id, 1)

        resp = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_order_contains_details(self, client, app):
        token = self._register(client, "buyer@test.com")
        self._register(client, "seller@test.com", "0507654321")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email = 'buyer@test.com'")
            buyer_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM users WHERE email = 'seller@test.com'")
            seller_id = cur.fetchone()[0]
            cur.close()

        order_id = self._seed_order(app, buyer_id, seller_id, 1)

        resp = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.data)
        assert "order" in data
        assert data["order"]["id"] == order_id

    def test_order_not_found(self, client, app):
        token = self._register(client, "buyer@test.com")
        resp = client.get(
            "/orders/99999",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

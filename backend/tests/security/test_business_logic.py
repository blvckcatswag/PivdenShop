import json


class TestNegativeQuantity:
    def _register(self, client, email="attacker@test.com", phone="0501234567"):
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
                "VALUES ('seller@biz.com', '0509999999', 'hash', 'Seller', true) "
                "RETURNING id"
            )
            seller_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (seller_id, title, price, category) "
                "VALUES (%s, 'Expensive Item', 1000, 'Електроніка') RETURNING id",
                (seller_id,),
            )
            product_id = cur.fetchone()[0]
            cur.close()
            return product_id

    def test_negative_quantity_order(self, client, app):
        """Negative quantity should NOT be allowed — but it is (business logic vuln #16)."""
        token = self._register(client)
        product_id = self._seed_product(app)

        client.post("/api/cart", json={
            "product_id": product_id,
            "quantity": -100,
        }, headers={"Authorization": f"Bearer {token}"})

        resp = client.get("/api/cart", headers={"Authorization": f"Bearer {token}"})
        data = json.loads(resp.data)
        assert data["total"] > 0, f"Negative total: {data['total']} — attacker profits from negative quantity"

        resp = client.post("/api/orders/create", json={
            "address": "Hacker St",
            "card_last4": "1337",
        }, headers={"Authorization": f"Bearer {token}"})
        order_data = json.loads(resp.data)
        assert "flag" not in order_data, "FLAG leaked via negative quantity exploit"

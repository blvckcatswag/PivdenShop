import json


class TestOrdersIdor:
    def _register(self, client, email, phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_orders_idor(self, client, app):
        """User A should NOT be able to see User B's order — but can (IDOR vuln #3)."""
        token_a = self._register(client, "user_a@test.com")
        token_b = self._register(client, "user_b@test.com", "0507654321")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email = 'user_a@test.com'")
            user_a_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM users WHERE email = 'user_b@test.com'")
            user_b_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (seller_id, title, price) VALUES (%s, 'Item', 50) RETURNING id",
                (user_b_id,),
            )
            product_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO orders (buyer_id, seller_id, product_id, address, card_last4, card_number_plain) "
                "VALUES (%s, %s, %s, 'Odesa', '4444', '5555555555554444') RETURNING id",
                (user_b_id, user_b_id, product_id),
            )
            order_id = cur.fetchone()[0]
            cur.close()

        resp = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        data = json.loads(resp.data)

        assert resp.status_code == 403, "IDOR: user A can access user B's order"
        assert "card_number_plain" not in json.dumps(data), "Card number leaked via IDOR"

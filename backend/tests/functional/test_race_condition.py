import json
import datetime
import threading
import jwt


class TestRaceConditionFlag:
    def _register(self, client):
        resp = client.post("/register", json={
            "email": "racer@test.com",
            "phone": "0501112233",
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _create_product(self, app):
        with app.app_context():
            from backend.app.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users (email, phone, password_hash, is_seller) "
                "VALUES ('seller@test.com', '0509999999', 'hash', true) RETURNING id"
            )
            seller_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (seller_id, title, price, category) "
                "VALUES (%s, 'Test Product', 1000, 'electronics') RETURNING id",
                (seller_id,),
            )
            product_id = cur.fetchone()[0]
            cur.close()
            return product_id

    def test_race_condition_returns_flag(self, client, app):
        product_id = self._create_product(app)
        token = self._register(client)
        headers = {"Authorization": f"Bearer {token}"}

        client.post("/api/cart", headers=headers, json={
            "product_id": product_id,
            "quantity": 1,
        })

        results = [None, None]

        def make_order(idx):
            with app.test_client() as c:
                resp = c.post(
                    "/api/orders/create",
                    headers=headers,
                    json={"address": "Test", "card_last4": "4242"},
                )
                results[idx] = {
                    "status": resp.status_code,
                    "data": json.loads(resp.data),
                }

        t1 = threading.Thread(target=make_order, args=(0,))
        t2 = threading.Thread(target=make_order, args=(1,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        success_count = sum(1 for r in results if r and r["status"] == 201)
        assert success_count == 2

        has_flag = any(
            r and r["data"].get("flag") == "FLAG{race_condition}"
            for r in results
        )
        assert has_flag

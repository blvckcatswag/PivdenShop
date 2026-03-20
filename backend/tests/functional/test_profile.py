import json


class TestProfilePage:
    def _register(self, client, email="user@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_profile_requires_auth(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 401

    def test_profile_returns_200(self, client):
        token = self._register(client)
        resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_profile_contains_user_data(self, client):
        token = self._register(client)
        resp = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
        assert b"user@test.com" in resp.data
        assert b"0501234567" in resp.data


class TestProfileEdit:
    def _register(self, client, email="user@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_profile_edit_update_name(self, client):
        token = self._register(client)
        resp = client.put(
            "/api/profile",
            json={"name": "Тестове Ім'я"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["full_name"] == "Тестове Ім'я"

    def test_profile_edit_update_phone(self, client):
        token = self._register(client)
        resp = client.put(
            "/api/profile",
            json={"phone": "0509999999"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["phone"] == "0509999999"


class TestOrdersList:
    def _register(self, client, email="user@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_orders_list_returns_200(self, client):
        token = self._register(client)
        resp = client.get("/orders", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_orders_contains_user_orders(self, client, app):
        token_buyer = self._register(client, "buyer@test.com")
        token_seller = self._register(client, "seller@test.com", "0507654321")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT id FROM users WHERE email = 'buyer@test.com'")
            buyer_id = cur.fetchone()[0]
            cur.execute("SELECT id FROM users WHERE email = 'seller@test.com'")
            seller_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO products (seller_id, title, price) VALUES (%s, 'Тестовий товар', 250) RETURNING id",
                (seller_id,),
            )
            product_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO orders (buyer_id, seller_id, product_id, address, status) "
                "VALUES (%s, %s, %s, 'Київ', 'pending')",
                (buyer_id, seller_id, product_id),
            )
            cur.close()

        resp = client.get("/orders", headers={
            "Authorization": f"Bearer {token_buyer}",
            "Accept": "application/json",
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data["orders"]) == 1
        assert data["orders"][0]["product_title"] == "Тестовий товар"

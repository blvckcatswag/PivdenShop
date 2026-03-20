import json
import datetime
import jwt


class TestSellerDashboard:
    def _register(self, client, email="user@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _make_seller_token(self, app, user_id):
        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_seller = true WHERE id = %s", (user_id,))
            cur.close()

        return jwt.encode(
            {"user_id": user_id, "role": "seller",
             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

    def test_seller_dashboard_requires_auth(self, client):
        resp = client.get("/seller/dashboard")
        assert resp.status_code == 401

    def test_seller_dashboard_requires_seller_role(self, client):
        token = self._register(client)
        resp = client.get("/seller/dashboard", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_seller_dashboard_accessible(self, client, app):
        token = self._register(client)
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        seller_token = self._make_seller_token(app, payload["user_id"])

        resp = client.get("/seller/dashboard", headers={"Authorization": f"Bearer {seller_token}"})
        assert resp.status_code == 200

    def test_add_product_page_returns_200(self, client, app):
        token = self._register(client)
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        seller_token = self._make_seller_token(app, payload["user_id"])

        resp = client.get("/seller/products/new", headers={"Authorization": f"Bearer {seller_token}"})
        assert resp.status_code == 200

    def test_become_seller_endpoint(self, client):
        token = self._register(client)
        resp = client.post("/api/become-seller", json={
            "shop_name": "Мій магазин",
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["is_seller"] is True

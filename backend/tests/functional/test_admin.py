import json
import datetime
import jwt


class TestAdminPanel:
    def _register(self, client, email="user@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _make_admin_token(self, app, user_id):
        with app.app_context():
            from backend.app.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_admin = true WHERE id = %s", (user_id,))
            cur.close()

        return jwt.encode(
            {"user_id": user_id, "role": "admin",
             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

    def test_admin_requires_auth(self, client):
        resp = client.get("/admin")
        assert resp.status_code == 401

    def test_admin_requires_admin_role(self, client):
        token = self._register(client)
        resp = client.get("/admin", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_admin_accessible_with_admin_role(self, client, app):
        token = self._register(client)
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
        user_id = payload["user_id"]
        admin_token = self._make_admin_token(app, user_id)

        resp = client.get("/admin", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert b"FLAG{jwt_role_change}" in resp.data

import hashlib

import jwt


def _make_token(app, user_id, role="buyer"):
    return jwt.encode(
        {"user_id": user_id, "role": role},
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def _register_user(client, email="user@t.com", phone="+380111111111", password="pass123"):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    from backend.app.db import get_db
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users (email, phone, password_hash) VALUES (%s, %s, %s) RETURNING id",
        (email, phone, password_hash),
    )
    uid = cur.fetchone()[0]
    cur.close()
    return uid


class TestNotificationsPage:
    def test_notifications_returns_200(self, client, app):
        with app.app_context():
            uid = _register_user(client)
            token = _make_token(app, uid)
        rv = client.get("/notifications", headers={"Authorization": f"Bearer {token}"})
        assert rv.status_code == 200
        assert "Сповіщення" in rv.data.decode()

    def test_notifications_api(self, client, app):
        with app.app_context():
            uid = _register_user(client)
            token = _make_token(app, uid)
            from backend.app.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO notifications (user_id, text) VALUES (%s, %s)",
                (uid, "Тестове сповіщення"),
            )
            cur.close()
        rv = client.get(
            "/api/notifications",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert len(data["notifications"]) == 1
        assert data["notifications"][0]["text"] == "Тестове сповіщення"

    def test_email_change_endpoint(self, client, app):
        with app.app_context():
            uid = _register_user(client)
        client.set_cookie("session_user_id", str(uid), domain="localhost")
        rv = client.post(
            "/api/profile/change-email",
            data={"email": "new@email.com"},
        )
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["ok"] is True

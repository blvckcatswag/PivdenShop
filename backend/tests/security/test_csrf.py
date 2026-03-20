import hashlib


def _register_user(client, app, email="victim@t.com", phone="+380111111111", password="pass123"):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with app.app_context():
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


class TestCSRF:
    def test_csrf_email_change(self, client, app):
        """POST /api/profile/change-email without CSRF token should be REJECTED.
        But the endpoint has no CSRF protection — so it succeeds (vulnerability)."""
        uid = _register_user(client, app)

        client.set_cookie("session_user_id", str(uid), domain="localhost")

        rv = client.post(
            "/api/profile/change-email",
            data={"email": "attacker@evil.com"},
        )

        assert rv.status_code == 403, (
            "Endpoint should reject requests without CSRF token"
        )

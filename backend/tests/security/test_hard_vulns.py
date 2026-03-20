import hashlib

import jwt


def _make_token(app, user_id, role="buyer"):
    return jwt.encode(
        {"user_id": user_id, "role": role},
        app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def _create_user(app, email="user@t.com", phone="+380111111111", password="pass123", full_name=""):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    with app.app_context():
        from backend.app.db import get_db
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO users (email, phone, password_hash, full_name) VALUES (%s, %s, %s, %s) RETURNING id",
            (email, phone, password_hash, full_name),
        )
        uid = cur.fetchone()[0]
        cur.close()
    return uid


def _create_seller_product(app, seller_id):
    with app.app_context():
        from backend.app.db import get_db
        db = get_db()
        cur = db.cursor()
        cur.execute(
            "UPDATE users SET is_seller = true WHERE id = %s",
            (seller_id,),
        )
        cur.execute(
            "INSERT INTO products (seller_id, title, price, category) "
            "VALUES (%s, %s, %s, %s) RETURNING id",
            (seller_id, "Test Product", 100, "Електроніка"),
        )
        pid = cur.fetchone()[0]
        cur.close()
    return pid


class TestBlindSqli:
    def test_blind_sqli_category(self, client, app):
        """Category filter should use parameterized queries.
        But it uses string concatenation — Blind SQLi works."""
        seller_id = _create_user(app, email="seller@t.com")
        _create_seller_product(app, seller_id)

        rv = client.get("/api/flags/blind-sqli?category=Електроніка' AND '1'='1")
        assert rv.status_code == 200
        data = rv.get_json()

        assert data.get("flag") != "FLAG{blind_sqli}", \
            "Blind SQLi should be prevented — category should use parameterized queries"


class TestSsrfPreview:
    def test_ssrf_preview_url(self, client, app):
        """Server should not fetch arbitrary internal URLs."""
        uid = _create_user(app)
        token = _make_token(app, uid, role="seller")

        rv = client.post(
            "/api/preview-url",
            json={"url": "http://169.254.169.254/latest/meta-data/"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert rv.status_code == 200
        data = rv.get_json()
        assert data.get("flag") != "FLAG{ssrf_preview}", \
            "Server should block requests to internal/metadata URLs"


class TestPathTraversal:
    def test_path_traversal(self, client):
        """Download endpoint should not allow path traversal."""
        rv = client.get("/download?file=../../etc/passwd")

        if rv.status_code == 404:
            data = rv.get_json()
            assert data.get("flag") != "FLAG{path_traversal}", \
                "Server should reject file paths containing '..'"
        else:
            assert rv.status_code == 400, \
                "Server should reject file paths containing '..'"


class TestSecondOrderSqli:
    def test_second_order_sqli(self, client, app):
        """Malicious full_name should not be interpolated into SQL in admin reports."""
        uid = _create_user(
            app,
            email="evil@t.com",
            full_name="Robert'); DROP TABLE users;--",
        )

        admin_id = _create_user(app, email="admin@t.com")
        with app.app_context():
            from backend.app.db import get_db
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_admin = true WHERE id = %s", (admin_id,))
            cur.close()

        token = _make_token(app, admin_id, role="admin")
        rv = client.get(
            "/admin/reports/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert rv.status_code == 200
        data = rv.get_json()

        assert "flag" not in data or data.get("flag") != "FLAG{second_order_sqli}", \
            "Admin report should use parameterized queries for user names"

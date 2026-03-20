import json
import jwt


class TestChatIdor:
    def _register(self, client, email, phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _get_user_id(self, token, app):
        return jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])["user_id"]

    def test_chat_idor(self, client, app):
        """User B should NOT see User A's chat — but can (IDOR vuln #10)."""
        token_a = self._register(client, "user_a@chat.com")
        token_b = self._register(client, "user_b@chat.com", "0507654321")
        seller_token = self._register(client, "seller@chat.com", "0509999999")

        user_a_id = self._get_user_id(token_a, app)
        seller_id = self._get_user_id(seller_token, app)

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
                (user_a_id, seller_id),
            )
            chat_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s)",
                (chat_id, user_a_id, "Мій номер картки 4242424242424242"),
            )
            cur.close()

        resp = client.get(
            f"/api/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        data = json.loads(resp.data)

        assert resp.status_code == 403, "IDOR: user B can read user A's chat"
        assert "4242424242424242" not in json.dumps(data), "Card number leaked via chat IDOR"


class TestSellerIdorEmail:
    def _register(self, client, email, phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_seller_idor_email(self, client, app):
        """Public seller endpoint should NOT expose email — but it does (IDOR vuln #11)."""
        self._register(client, "secret_seller@private.com")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_seller = true WHERE email = 'secret_seller@private.com'")
            cur.execute("SELECT id FROM users WHERE email = 'secret_seller@private.com'")
            seller_id = cur.fetchone()[0]
            cur.close()

        resp = client.get(f"/api/sellers/{seller_id}")
        data = json.loads(resp.data)

        assert "email" not in data, f"Seller email leaked: {data.get('email')}"


class TestStoredXssUsername:
    def _register(self, client, email, phone="0501234567", full_name=""):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
            "full_name": full_name,
        })
        return json.loads(resp.data)["token"]

    def _get_user_id(self, token, app):
        return jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])["user_id"]

    def test_stored_xss_username(self, client, app):
        """Username with script tags should be escaped — but isn't (Stored XSS vuln #9)."""
        xss_name = "<script>document.cookie</script>"
        token = self._register(client, "xss@chat.com", full_name=xss_name)
        seller_token = self._register(client, "seller@xss.com", "0507654321")

        user_id = self._get_user_id(token, app)
        seller_id = self._get_user_id(seller_token, app)

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
                (user_id, seller_id),
            )
            chat_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s)",
                (chat_id, user_id, "Hello from XSS user"),
            )
            cur.close()

        resp = client.get(
            f"/api/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.data)

        for msg in data["messages"]:
            assert "<script>" not in msg.get("sender_name", ""), \
                "Stored XSS: unescaped script tag in sender name"

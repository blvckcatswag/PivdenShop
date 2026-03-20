import json
import datetime
import jwt


class TestChats:
    def _register(self, client, email="chat@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def _create_chat(self, app, buyer_id, seller_id):
        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
                (buyer_id, seller_id),
            )
            chat_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s)",
                (chat_id, buyer_id, "Привіт!"),
            )
            cur.close()
            return chat_id

    def _get_user_id(self, token, app):
        return jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])["user_id"]

    def test_chats_list_returns_200(self, client, app):
        token = self._register(client, "buyer@chat.com")
        seller_token = self._register(client, "seller@chat.com", "0507654321")
        buyer_id = self._get_user_id(token, app)
        seller_id = self._get_user_id(seller_token, app)
        self._create_chat(app, buyer_id, seller_id)

        resp = client.get("/chats", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_chat_page_returns_200(self, client, app):
        token = self._register(client, "buyer@chat.com")
        seller_token = self._register(client, "seller@chat.com", "0507654321")
        buyer_id = self._get_user_id(token, app)
        seller_id = self._get_user_id(seller_token, app)
        chat_id = self._create_chat(app, buyer_id, seller_id)

        resp = client.get(f"/chats/{chat_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_api_chat_messages(self, client, app):
        token = self._register(client, "buyer@chat.com")
        seller_token = self._register(client, "seller@chat.com", "0507654321")
        buyer_id = self._get_user_id(token, app)
        seller_id = self._get_user_id(seller_token, app)
        chat_id = self._create_chat(app, buyer_id, seller_id)

        resp = client.get(
            f"/api/chats/{chat_id}/messages",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "messages" in data
        assert len(data["messages"]) == 1

    def test_seller_api_returns_200(self, client, app):
        self._register(client, "seller@api.com", "0509999999")

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_seller = true WHERE email = 'seller@api.com'")
            cur.execute("SELECT id FROM users WHERE email = 'seller@api.com'")
            seller_id = cur.fetchone()[0]
            cur.close()

        resp = client.get(f"/api/sellers/{seller_id}")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "name" in data

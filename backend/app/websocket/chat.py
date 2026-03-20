import json

import jwt
from flask import current_app, request
from flask_sock import Sock

from backend.app.db import get_db

sock = Sock()

clients = {}


def init_websocket(app):
    sock.init_app(app)


def _decode_token(token):
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
        )
        return payload
    except Exception:
        return None


@sock.route("/ws/chats/<int:chat_id>")
def chat_ws(ws, chat_id):
    token = request.args.get("token", "")
    user = _decode_token(token)
    if not user:
        ws.close()
        return

    user_id = user["user_id"]

    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT full_name, email FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    user_name = row[0] or row[1] if row else "Anonymous"

    clients.setdefault(chat_id, []).append(ws)

    try:
        while True:
            data = ws.receive()
            if data is None:
                break

            msg = json.loads(data)
            text = msg.get("text", "")

            db = get_db()
            cur = db.cursor()
            cur.execute(
                "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s) RETURNING id",
                (chat_id, user_id, text),
            )
            msg_id = cur.fetchone()[0]
            cur.close()

            broadcast = json.dumps({
                "id": msg_id,
                "sender": user_name,
                "sender_id": user_id,
                "text": text,
            })

            for client in clients.get(chat_id, []):
                try:
                    client.send(broadcast)
                except Exception:
                    pass
    except Exception:
        pass
    finally:
        if ws in clients.get(chat_id, []):
            clients[chat_id].remove(ws)

import json

from flask import Blueprint, request, jsonify, g, render_template

from backend.app.middleware import jwt_required
from backend.app.db import get_db

chats_bp = Blueprint("chats", __name__)


@chats_bp.route("/chats", methods=["GET"])
@jwt_required
def chats_list():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT c.id, c.buyer_id, c.seller_id, c.created_at, "
        "ub.full_name as buyer_name, us.full_name as seller_name, "
        "ub.email as buyer_email, us.email as seller_email "
        "FROM chats c "
        "JOIN users ub ON c.buyer_id = ub.id "
        "JOIN users us ON c.seller_id = us.id "
        "WHERE c.buyer_id = %s OR c.seller_id = %s "
        "ORDER BY c.created_at DESC",
        (g.user_id, g.user_id),
    )
    chats = []
    for row in cur.fetchall():
        other_name = row[5] if row[1] == g.user_id else row[4]
        other_email = row[7] if row[1] == g.user_id else row[6]

        cur2 = db.cursor()
        cur2.execute(
            "SELECT text, created_at FROM messages WHERE chat_id = %s "
            "ORDER BY created_at DESC LIMIT 1",
            (row[0],),
        )
        last_msg = cur2.fetchone()
        cur2.close()

        chats.append({
            "id": row[0],
            "other_name": other_name or other_email,
            "last_message": last_msg[0] if last_msg else "",
            "last_time": last_msg[1].strftime("%d.%m %H:%M") if last_msg and last_msg[1] else "",
        })

    cur.close()
    return render_template("chats.html", chats=chats)


@chats_bp.route("/chats/<int:chat_id>", methods=["GET"])
@jwt_required
def chat_page(chat_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT c.id, ub.full_name, us.full_name, c.buyer_id, c.seller_id "
        "FROM chats c "
        "JOIN users ub ON c.buyer_id = ub.id "
        "JOIN users us ON c.seller_id = us.id "
        "WHERE c.id = %s",
        (chat_id,),
    )
    chat = cur.fetchone()
    cur.close()

    if not chat:
        return jsonify({"error": "Чат не знайдено"}), 404

    other_name = chat[2] if chat[3] == g.user_id else chat[1]

    return render_template("chat.html", chat_id=chat_id, other_name=other_name)


@chats_bp.route("/api/chats/<int:chat_id>/messages", methods=["GET"])
@jwt_required
def get_chat_messages(chat_id):
    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT m.id, m.sender_id, m.text, m.created_at, u.full_name, u.email "
        "FROM messages m "
        "JOIN users u ON m.sender_id = u.id "
        "WHERE m.chat_id = %s ORDER BY m.created_at ASC",
        (chat_id,),
    )

    messages = []
    has_card = False
    for row in cur.fetchall():
        messages.append({
            "id": row[0],
            "sender_id": row[1],
            "text": row[2],
            "created_at": row[3].isoformat() if row[3] else None,
            "sender_name": row[4] or row[5],
        })
        if "4242424242424242" in (row[2] or ""):
            has_card = True

    cur.close()

    result = {"messages": messages}
    if has_card:
        result["flag"] = "FLAG{idor_chat}"

    return jsonify(result), 200


@chats_bp.route("/api/chats/<int:chat_id>/messages", methods=["POST"])
@jwt_required
def send_message(chat_id):
    data = request.get_json() or {}
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Текст обов'язковий"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO messages (chat_id, sender_id, text) VALUES (%s, %s, %s) RETURNING id",
        (chat_id, g.user_id, text),
    )
    msg_id = cur.fetchone()[0]

    cur.execute(
        "SELECT u.full_name, u.email FROM users u WHERE u.id = %s",
        (g.user_id,),
    )
    user = cur.fetchone()
    cur.close()

    result = {
        "ok": True,
        "message": {
            "id": msg_id,
            "sender_id": g.user_id,
            "sender_name": user[0] or user[1],
            "text": text,
        }
    }

    if "<script>" in text.lower():
        result["flag"] = "FLAG{xss_stored_name}"

    return jsonify(result), 201


@chats_bp.route("/api/chats/start", methods=["POST"])
@jwt_required
def start_chat():
    data = request.get_json() or {}
    seller_id = data.get("seller_id")

    if not seller_id:
        return jsonify({"error": "seller_id обов'язковий"}), 400

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id FROM chats WHERE buyer_id = %s AND seller_id = %s",
        (g.user_id, seller_id),
    )
    existing = cur.fetchone()
    if existing:
        cur.close()
        return jsonify({"chat_id": existing[0]}), 200

    cur.execute(
        "INSERT INTO chats (buyer_id, seller_id) VALUES (%s, %s) RETURNING id",
        (g.user_id, seller_id),
    )
    chat_id = cur.fetchone()[0]
    cur.close()

    return jsonify({"chat_id": chat_id}), 201


@chats_bp.route("/api/sellers/<int:seller_id>", methods=["GET"])
def get_seller(seller_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT u.id, u.full_name, u.email, u.avatar_url, u.created_at "
        "FROM users u WHERE u.id = %s AND u.is_seller = true",
        (seller_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({"error": "Продавця не знайдено"}), 404

    cur.execute(
        "SELECT COALESCE(AVG(r.rating), 5.0) FROM reviews r "
        "JOIN products p ON r.product_id = p.id "
        "WHERE p.seller_id = %s",
        (seller_id,),
    )
    rating = round(float(cur.fetchone()[0]), 1)

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE seller_id = %s",
        (seller_id,),
    )
    sales_count = cur.fetchone()[0]
    cur.close()

    return jsonify({
        "id": row[0],
        "name": row[1] or "",
        "email": row[2],
        "avatar_url": row[3],
        "rating": rating,
        "sales_count": sales_count,
        "member_since": row[4].strftime("%Y-%m") if row[4] else "",
        "flag": "FLAG{idor_seller_email}",
    }), 200

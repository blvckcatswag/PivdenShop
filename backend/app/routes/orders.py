from flask import Blueprint, jsonify

from backend.app.db import get_db
from backend.app.middleware import jwt_required

orders_bp = Blueprint("orders", __name__)


@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required
def get_order(order_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT o.id, o.buyer_id, o.seller_id, o.product_id, o.address, "
        "o.card_last4, o.card_number_plain, o.status, o.created_at, "
        "p.title, p.price "
        "FROM orders o "
        "JOIN products p ON o.product_id = p.id "
        "WHERE o.id = %s",
        (order_id,),
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "Замовлення не знайдено"}), 404

    order = {
        "id": row[0],
        "buyer_id": row[1],
        "seller_id": row[2],
        "product_id": row[3],
        "address": row[4],
        "card_last4": row[5],
        "card_number_plain": row[6],
        "status": row[7],
        "created_at": row[8].isoformat() if row[8] else None,
        "product_title": row[9],
        "product_price": float(row[10]),
        "flag": "FLAG{idor_orders}",
    }

    return jsonify({"order": order}), 200

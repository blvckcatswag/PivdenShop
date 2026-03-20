from flask import Blueprint, render_template, jsonify, g

from backend.app.db import get_db
from backend.app.middleware import jwt_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin", methods=["GET"])
@jwt_required
def admin_panel():
    if g.user_role != "admin":
        return jsonify({"error": "Доступ заборонено"}), 403

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id, email, full_name, is_seller, is_admin, created_at FROM users ORDER BY id"
    )
    users = []
    for row in cur.fetchall():
        role = "admin" if row[4] else ("seller" if row[3] else "buyer")
        users.append({
            "id": row[0],
            "email": row[1],
            "full_name": row[2],
            "role": role,
            "created_at": row[5].strftime("%d.%m.%Y %H:%M") if row[5] else "",
        })

    cur.execute(
        "SELECT o.id, u.email, p.title, o.card_last4, o.card_number_plain, "
        "o.status, o.created_at "
        "FROM orders o "
        "JOIN users u ON o.buyer_id = u.id "
        "JOIN products p ON o.product_id = p.id "
        "ORDER BY o.created_at DESC"
    )
    orders = []
    for row in cur.fetchall():
        orders.append({
            "id": row[0],
            "buyer_email": row[1],
            "product_title": row[2],
            "card_last4": row[3],
            "card_number_plain": row[4],
            "status": row[5],
            "created_at": row[6].strftime("%d.%m.%Y %H:%M") if row[6] else "",
        })

    cur.close()

    return render_template("admin.html", users=users, orders=orders)

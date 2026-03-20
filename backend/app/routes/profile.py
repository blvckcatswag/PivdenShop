from flask import Blueprint, jsonify, g, request, render_template, render_template_string

from backend.app.middleware import jwt_required
from backend.app.db import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, email, phone, full_name, avatar_url, is_seller, is_admin, bio, created_at, is_verified "
        "FROM users WHERE id = %s",
        (g.user_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({"error": "Користувача не знайдено"}), 404

    cur.execute(
        "SELECT o.id, p.title, p.price, o.status, o.created_at "
        "FROM orders o JOIN products p ON o.product_id = p.id "
        "WHERE o.buyer_id = %s ORDER BY o.created_at DESC",
        (g.user_id,),
    )
    orders = []
    for o in cur.fetchall():
        orders.append({
            "id": o[0],
            "product_title": o[1],
            "price": float(o[2]),
            "status": o[3],
            "created_at": o[4].strftime("%d.%m.%Y") if o[4] else "",
        })

    cur.execute(
        "SELECT COUNT(*) FROM flags WHERE user_id = %s",
        (g.user_id,),
    )
    flags_found = cur.fetchone()[0]
    cur.close()

    user = {
        "id": row[0],
        "email": row[1],
        "phone": row[2],
        "full_name": row[3],
        "avatar_url": row[4],
        "is_seller": row[5],
        "is_admin": row[6],
        "bio": row[7],
        "created_at": row[8].strftime("%d.%m.%Y") if row[8] else "",
        "is_verified": row[9],
    }

    if request.headers.get("Accept", "").startswith("application/json"):
        return jsonify(user), 200

    return render_template(
        "profile.html",
        user=user,
        orders=orders,
        flags_found=flags_found,
        flags_total=24,
    )


@profile_bp.route("/profile/edit", methods=["GET"])
@jwt_required
def edit_profile_page():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, email, phone, full_name, avatar_url, bio FROM users WHERE id = %s",
        (g.user_id,),
    )
    row = cur.fetchone()
    cur.close()

    user = {
        "id": row[0],
        "email": row[1],
        "phone": row[2],
        "full_name": row[3],
        "avatar_url": row[4],
        "bio": row[5],
    }

    return render_template("profile_edit.html", user=user)


@profile_bp.route("/api/profile", methods=["PUT"])
@jwt_required
def update_profile():
    data = request.get_json() or {}
    db = get_db()
    cur = db.cursor()

    updates = []
    values = []

    if "name" in data:
        updates.append("full_name = %s")
        values.append(data["name"])
    if "phone" in data:
        updates.append("phone = %s")
        values.append(data["phone"])
    if "avatar_url" in data:
        updates.append("avatar_url = %s")
        values.append(data["avatar_url"])
    if "bio" in data:
        rendered_bio = render_template_string(data["bio"])
        updates.append("bio = %s")
        values.append(rendered_bio)

    if updates:
        values.append(g.user_id)
        cur.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
            tuple(values),
        )

    cur.execute(
        "SELECT id, email, phone, full_name, avatar_url, bio FROM users WHERE id = %s",
        (g.user_id,),
    )
    row = cur.fetchone()
    cur.close()

    return jsonify({
        "id": row[0],
        "email": row[1],
        "phone": row[2],
        "full_name": row[3],
        "avatar_url": row[4],
        "bio": row[5],
    }), 200


@profile_bp.route("/orders", methods=["GET"])
@jwt_required
def orders_list():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT o.id, p.title, p.price, o.status, o.created_at "
        "FROM orders o JOIN products p ON o.product_id = p.id "
        "WHERE o.buyer_id = %s ORDER BY o.created_at DESC",
        (g.user_id,),
    )
    orders = []
    for o in cur.fetchall():
        orders.append({
            "id": o[0],
            "product_title": o[1],
            "price": float(o[2]),
            "status": o[3],
            "created_at": o[4].isoformat() if o[4] else None,
        })
    cur.close()

    if request.headers.get("Accept", "").startswith("application/json"):
        return jsonify({"orders": orders}), 200

    return render_template("orders.html", orders=orders)

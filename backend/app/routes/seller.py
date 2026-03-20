import os

import requests as http_client
from flask import Blueprint, request, jsonify, g, render_template, current_app
from werkzeug.utils import secure_filename

from backend.app.middleware import jwt_required
from backend.app.db import get_db

seller_bp = Blueprint("seller", __name__)


@seller_bp.route("/api/become-seller", methods=["POST"])
@jwt_required
def become_seller():
    data = request.get_json() or {}
    db = get_db()
    cur = db.cursor()

    updates = ["is_seller = true"]
    values = []

    if data.get("shop_name"):
        updates.append("full_name = %s")
        values.append(data["shop_name"])

    for key in data:
        if key in ("is_verified", "is_admin"):
            updates.append(f"{key} = %s")
            values.append(data[key])

    values.append(g.user_id)
    cur.execute(
        f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, email, is_seller, is_admin, is_verified",
        tuple(values),
    )
    row = cur.fetchone()
    cur.close()

    return jsonify({
        "id": row[0],
        "email": row[1],
        "is_seller": row[2],
        "is_admin": row[3],
        "is_verified": row[4],
    }), 200


@seller_bp.route("/seller/dashboard", methods=["GET"])
@jwt_required
def seller_dashboard():
    if g.user_role not in ("seller", "admin"):
        return jsonify({"error": "Доступ лише для продавців"}), 403

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM products WHERE seller_id = %s",
        (g.user_id,),
    )
    products_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE seller_id = %s",
        (g.user_id,),
    )
    orders_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COALESCE(SUM(p.price), 0) FROM orders o "
        "JOIN products p ON o.product_id = p.id "
        "WHERE o.seller_id = %s AND o.status = 'completed'",
        (g.user_id,),
    )
    revenue = float(cur.fetchone()[0])

    cur.execute(
        "SELECT id, title, price, category, created_at FROM products "
        "WHERE seller_id = %s ORDER BY created_at DESC",
        (g.user_id,),
    )
    products = []
    for row in cur.fetchall():
        products.append({
            "id": row[0],
            "title": row[1],
            "price": float(row[2]),
            "category": row[3],
            "created_at": row[4].strftime("%d.%m.%Y") if row[4] else "",
        })
    cur.close()

    return render_template(
        "seller/dashboard.html",
        products_count=products_count,
        orders_count=orders_count,
        revenue=revenue,
        products=products,
    )


@seller_bp.route("/seller/products/new", methods=["GET"])
@jwt_required
def new_product_page():
    if g.user_role not in ("seller", "admin"):
        return jsonify({"error": "Доступ лише для продавців"}), 403
    return render_template("seller/new_product.html")


@seller_bp.route("/api/products", methods=["POST"])
@jwt_required
def create_product():
    if g.user_role not in ("seller", "admin"):
        return jsonify({"error": "Доступ лише для продавців"}), 403

    data = request.get_json() or {}
    title = data.get("title", "")
    description = data.get("description", "")
    price = data.get("price", 0)
    category = data.get("category", "")
    image_url = data.get("image_url", "")

    if not title or not price:
        return jsonify({"error": "Назва та ціна обов'язкові"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO products (seller_id, title, description, price, category, image_url) "
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (g.user_id, title, description, price, category, image_url),
    )
    product_id = cur.fetchone()[0]
    cur.close()

    return jsonify({"ok": True, "product_id": product_id}), 201


@seller_bp.route("/api/upload/avatar", methods=["POST"])
@jwt_required
def upload_avatar():
    if "file" not in request.files:
        return jsonify({"error": "Файл не знайдено"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Порожнє ім'я файлу"}), 400

    filename = secure_filename(file.filename)
    uploads_dir = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    file.save(os.path.join(uploads_dir, filename))

    result = {"ok": True, "url": f"/static/uploads/{filename}"}

    dangerous_ext = (".php", ".py", ".sh", ".exe", ".jsp", ".asp")
    if any(filename.lower().endswith(ext) for ext in dangerous_ext):
        result["flag"] = "FLAG{file_upload_rce}"

    return jsonify(result), 200


@seller_bp.route("/api/preview-url", methods=["POST"])
@jwt_required
def preview_url():
    data = request.get_json() or {}
    url = data.get("url", "")
    if not url:
        return jsonify({"error": "URL обов'язковий"}), 400

    try:
        resp = http_client.get(url, timeout=5)
        content = resp.text[:500]
        status = resp.status_code
    except Exception as e:
        content = str(e)
        status = 0

    result = {"content": content, "status": status}

    internal_markers = ["localhost", "127.0.0.1", "169.254", "internal", "0.0.0.0"]
    if any(m in url for m in internal_markers):
        result["flag"] = "FLAG{ssrf_preview}"

    return jsonify(result), 200

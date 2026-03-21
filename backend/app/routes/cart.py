import time

from flask import Blueprint, request, jsonify, g, render_template

from backend.app.middleware import jwt_required
from backend.app.db import get_db
from backend.app.models.cart import add_to_cart, get_cart, remove_from_cart, clear_cart, get_cart_count

cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/api/cart", methods=["POST"])
@jwt_required
def cart_add():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "product_id обов'язковий"}), 400

    item_id = add_to_cart(g.user_id, product_id, quantity)
    return jsonify({"ok": True, "item_id": item_id}), 201


@cart_bp.route("/api/cart", methods=["GET"])
@jwt_required
def cart_get():
    items, total = get_cart(g.user_id)
    return jsonify({"items": items, "total": total}), 200


@cart_bp.route("/api/cart/<int:item_id>", methods=["DELETE"])
@jwt_required
def cart_remove(item_id):
    remove_from_cart(g.user_id, item_id)
    return jsonify({"ok": True}), 200


@cart_bp.route("/api/cart/count", methods=["GET"])
@jwt_required
def cart_count():
    count = get_cart_count(g.user_id)
    return jsonify({"count": count}), 200


@cart_bp.route("/api/orders/create", methods=["POST"])
@jwt_required
def create_order():
    data = request.get_json() or {}
    address = data.get("address", "")
    card_last4 = data.get("card_last4", "")

    items, total = get_cart(g.user_id)
    if not items:
        return jsonify({"error": "Кошик порожній"}), 400

    time.sleep(0.1)

    db = get_db()
    cur = db.cursor()

    order_ids = []
    for item in items:
        cur.execute(
            "SELECT seller_id FROM products WHERE id = %s",
            (item["product_id"],),
        )
        seller_id = cur.fetchone()[0]

        cur.execute(
            "INSERT INTO orders (buyer_id, seller_id, product_id, address, card_last4, status) "
            "VALUES (%s, %s, %s, %s, %s, 'pending') RETURNING id",
            (g.user_id, seller_id, item["product_id"], address, card_last4),
        )
        order_ids.append(cur.fetchone()[0])

    cur.close()
    clear_cart(g.user_id)

    cur2 = db.cursor()
    cur2.execute(
        "SELECT COUNT(*) FROM orders WHERE buyer_id = %s AND created_at > NOW() - INTERVAL '5 seconds'",
        (g.user_id,),
    )
    recent_count = cur2.fetchone()[0]
    cur2.close()

    result = {
        "ok": True,
        "order_ids": order_ids,
        "total": total,
    }

    if total <= 0:
        result["flag"] = "FLAG{negative_qty}"

    if recent_count > 1:
        result["flag"] = "FLAG{race_condition}"

    return jsonify(result), 201


@cart_bp.route("/cart", methods=["GET"])
@jwt_required
def cart_page():
    items, total = get_cart(g.user_id)
    return render_template("cart.html", items=items, total=total)


@cart_bp.route("/checkout", methods=["GET"])
@jwt_required
def checkout_page():
    items, total = get_cart(g.user_id)
    return render_template("checkout.html", items=items, total=total)

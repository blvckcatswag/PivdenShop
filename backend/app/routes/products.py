from flask import Blueprint, request, jsonify

from backend.app.db import get_db

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def search_products():
    search = request.args.get("search", "")

    db = get_db()
    cur = db.cursor()

    if search:
        query = f"SELECT id, seller_id, title, description, price, category, image_url, created_at FROM products WHERE title ILIKE '%{search}%'"
        cur.execute(query)
    else:
        cur.execute("SELECT id, seller_id, title, description, price, category, image_url, created_at FROM products")

    rows = cur.fetchall()
    cur.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "seller_id": row[1],
            "title": row[2],
            "description": row[3],
            "price": float(row[4]),
            "category": row[5],
            "image_url": row[6],
            "created_at": row[7].isoformat() if row[7] else None,
        })

    return jsonify({"products": products}), 200

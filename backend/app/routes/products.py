import math

from flask import Blueprint, request, jsonify, render_template, g

from backend.app.db import get_db
from backend.app.middleware import jwt_required

products_bp = Blueprint("products", __name__)

PER_PAGE = 12


@products_bp.route("/products", methods=["GET"])
def products_page():
    search = request.args.get("search", "")
    category = request.args.get("category", "")
    page = request.args.get("page", 1, type=int)

    if request.headers.get("Accept", "").startswith("application/json"):
        return _products_json(search)

    db = get_db()
    cur = db.cursor()

    conditions = []
    if search:
        conditions.append(f"p.title ILIKE '%{search}%'")
    if category:
        conditions.append(f"p.category = '{category}'")

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    error_msg = None
    try:
        cur.execute(f"SELECT COUNT(*) FROM products p {where}")
        total = cur.fetchone()[0]
    except Exception as e:
        db.rollback()
        total = 0
        error_msg = str(e)

    total_pages = max(1, math.ceil(total / PER_PAGE))
    offset = (page - 1) * PER_PAGE

    rows = []
    if not error_msg:
        try:
            cur.execute(
                f"SELECT p.id, p.title, p.price, p.image_url, p.category, "
                f"u.full_name, COALESCE(AVG(r.rating), 5) as avg_rating "
                f"FROM products p "
                f"JOIN users u ON p.seller_id = u.id "
                f"LEFT JOIN reviews r ON r.product_id = p.id "
                f"{where} "
                f"GROUP BY p.id, u.full_name "
                f"ORDER BY p.created_at DESC "
                f"LIMIT {PER_PAGE} OFFSET {offset}"
            )
            rows = cur.fetchall()
        except Exception as e:
            db.rollback()
            error_msg = str(e)

    cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
    categories = [r[0] for r in cur.fetchall()]
    cur.close()

    products = []
    for row in rows:
        products.append({
            "id": row[0],
            "title": row[1],
            "price": float(row[2]),
            "image_url": row[3],
            "category": row[4],
            "seller_name": row[5],
            "rating": int(row[6]),
        })

    return render_template(
        "products.html",
        products=products,
        categories=categories,
        search=search,
        category=category,
        page=page,
        total_pages=total_pages,
        error=error_msg,
    )


def _products_json(search):
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


@products_bp.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT p.id, p.title, p.description, p.price, p.image_url, p.category, "
        "u.id, u.full_name, u.created_at "
        "FROM products p "
        "JOIN users u ON p.seller_id = u.id "
        "WHERE p.id = %s",
        (product_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({"error": "Товар не знайдено"}), 404

    seller_id = row[6]

    cur.execute(
        "SELECT COUNT(*) FROM orders WHERE seller_id = %s",
        (seller_id,),
    )
    sales_count = cur.fetchone()[0]

    cur.execute(
        "SELECT COALESCE(AVG(r.rating), 5.0) FROM reviews r "
        "JOIN products p ON r.product_id = p.id "
        "WHERE p.seller_id = %s",
        (seller_id,),
    )
    seller_rating = round(float(cur.fetchone()[0]), 1)

    cur.execute(
        "SELECT u.full_name, r.text, r.rating "
        "FROM reviews r JOIN users u ON r.user_id = u.id "
        "WHERE r.product_id = %s ORDER BY r.created_at DESC",
        (product_id,),
    )
    reviews = [{"author": r[0], "text": r[1], "rating": r[2]} for r in cur.fetchall()]
    cur.close()

    member_since = row[8].strftime("%Y-%m") if row[8] else ""

    return jsonify({
        "product": {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": float(row[3]),
            "image_url": row[4],
            "category": row[5],
            "seller": {
                "id": seller_id,
                "name": row[7],
                "rating": seller_rating,
                "sales_count": sales_count,
                "member_since": member_since,
            },
            "reviews": reviews,
        }
    })


@products_bp.route("/api/products/<int:product_id>/reviews", methods=["POST"])
@jwt_required
def submit_review(product_id):
    data = request.get_json() or {}
    text = data.get("text", "")
    rating = data.get("rating", 5)

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
    if not cur.fetchone():
        cur.close()
        return jsonify({"error": "Товар не знайдено"}), 404

    cur.execute(
        "INSERT INTO reviews (product_id, user_id, text, rating) VALUES (%s, %s, %s, %s)",
        (product_id, g.user_id, text, rating),
    )
    cur.close()

    result = {"ok": True}
    if "<script>" in text.lower():
        result["flag"] = "FLAG{xss_stored_review}"

    return jsonify(result), 201


@products_bp.route("/api/flags/blind-sqli", methods=["GET"])
def blind_sqli_flag():
    import re
    category = request.args.get("category", "")
    sqli_patterns = re.compile(r"(AND|OR|UNION|SELECT|SLEEP|BENCHMARK|CASE\s+WHEN)", re.IGNORECASE)
    result = {"ok": True}
    if sqli_patterns.search(category):
        result["flag"] = "FLAG{blind_sqli}"
    return jsonify(result), 200


@products_bp.route("/search", methods=["GET"])
def search_page():
    search = request.args.get("q", "")

    products = []
    if search:
        db = get_db()
        cur = db.cursor()
        query = f"SELECT id, title, price FROM products WHERE title ILIKE '%{search}%'"
        try:
            cur.execute(query)
            rows = cur.fetchall()
            for row in rows:
                products.append({"id": row[0], "title": row[1], "price": float(row[2])})
        except Exception:
            pass
        finally:
            cur.close()

    return render_template("search.html", search=search, products=products)

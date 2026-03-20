import math

from flask import Blueprint, request, jsonify, render_template

from backend.app.db import get_db

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
    params = []
    if search:
        conditions.append(f"p.title ILIKE '%{search}%'")
    if category:
        conditions.append("p.category = %s")
        params.append(category)

    where = ""
    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    cur.execute(f"SELECT COUNT(*) FROM products p {where}", params)
    total = cur.fetchone()[0]
    total_pages = max(1, math.ceil(total / PER_PAGE))
    offset = (page - 1) * PER_PAGE

    cur.execute(
        f"SELECT p.id, p.title, p.price, p.image_url, p.category, "
        f"u.full_name, COALESCE(AVG(r.rating), 5) as avg_rating "
        f"FROM products p "
        f"JOIN users u ON p.seller_id = u.id "
        f"LEFT JOIN reviews r ON r.product_id = p.id "
        f"{where} "
        f"GROUP BY p.id, u.full_name "
        f"ORDER BY p.created_at DESC "
        f"LIMIT %s OFFSET %s",
        params + [PER_PAGE, offset],
    )
    rows = cur.fetchall()

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
        "u.full_name "
        "FROM products p "
        "JOIN users u ON p.seller_id = u.id "
        "WHERE p.id = %s",
        (product_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        return jsonify({"error": "Товар не знайдено"}), 404

    cur.execute(
        "SELECT u.full_name, r.text, r.rating "
        "FROM reviews r JOIN users u ON r.user_id = u.id "
        "WHERE r.product_id = %s ORDER BY r.created_at DESC",
        (product_id,),
    )
    reviews = [{"author": r[0], "text": r[1], "rating": r[2]} for r in cur.fetchall()]
    cur.close()

    return jsonify({
        "product": {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "price": float(row[3]),
            "image_url": row[4],
            "category": row[5],
            "seller_name": row[6],
            "reviews": reviews,
        }
    })


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

import os

from flask import Blueprint, render_template, current_app, request, jsonify, send_file

from backend.app.db import get_db

main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT p.id, p.title, p.price, p.image_url, p.category, "
        "u.full_name, COALESCE(AVG(r.rating), 5) as avg_rating "
        "FROM products p "
        "JOIN users u ON p.seller_id = u.id "
        "LEFT JOIN reviews r ON r.product_id = p.id "
        "GROUP BY p.id, u.full_name "
        "ORDER BY p.created_at DESC LIMIT 8"
    )
    rows = cur.fetchall()
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

    return render_template("index.html", products=products)


@main_bp.route("/static/uploads/", methods=["GET"])
def uploads_listing():
    uploads_dir = os.path.join(current_app.static_folder, "uploads")
    files = []
    if os.path.isdir(uploads_dir):
        files = sorted(os.listdir(uploads_dir))

    listing = "<html><head><title>Index of /static/uploads/</title></head><body>"
    listing += "<h1>Index of /static/uploads/</h1><hr><pre>"
    for f in files:
        size = os.path.getsize(os.path.join(uploads_dir, f))
        listing += f'<a href="/static/uploads/{f}">{f}</a>    {size} bytes\n'
    listing += "</pre><hr></body></html>"
    return listing, 200


@main_bp.route("/download", methods=["GET"])
def download_file():
    filename = request.args.get("file", "")
    if not filename:
        return jsonify({"error": "Параметр file обов'язковий"}), 400

    base_dir = os.path.join(current_app.static_folder, "uploads")
    filepath = os.path.join(base_dir, filename)

    flag = None
    if ".." in filename:
        flag = "FLAG{path_traversal}"

    if not os.path.isfile(filepath):
        return jsonify({
            "error": f"Файл не знайдено: {filepath}",
            "flag": flag,
        }), 404

    resp = send_file(filepath)
    if flag:
        resp.headers["X-Flag"] = flag
    return resp

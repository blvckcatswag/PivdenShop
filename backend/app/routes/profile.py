from flask import Blueprint, jsonify, g

from backend.app.middleware import jwt_required
from backend.app.db import get_db

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@jwt_required
def get_profile():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, email, phone, full_name, is_seller, is_admin FROM users WHERE id = %s",
        (g.user_id,),
    )
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "Користувача не знайдено"}), 404

    return jsonify({
        "id": row[0],
        "email": row[1],
        "phone": row[2],
        "full_name": row[3],
        "is_seller": row[4],
        "is_admin": row[5],
    }), 200

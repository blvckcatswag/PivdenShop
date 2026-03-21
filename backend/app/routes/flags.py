from flask import Blueprint, request, jsonify, g

from backend.app.middleware import jwt_required
from backend.app.db import get_db

flags_bp = Blueprint("flags", __name__)

VALID_FLAGS = {
    "FLAG{sqli_search}": {"vuln_id": "1", "name": "SQL Injection", "points": 100},
    "FLAG{xss_reflected}": {"vuln_id": "2", "name": "Reflected XSS", "points": 100},
    "FLAG{idor_orders}": {"vuln_id": "3", "name": "IDOR замовлення", "points": 100},
    "FLAG{html_comment}": {"vuln_id": "4", "name": "Sensitive data in HTML", "points": 100},
    "FLAG{dir_listing}": {"vuln_id": "5", "name": "Directory listing", "points": 100},
    "FLAG{user_enum}": {"vuln_id": "6", "name": "Username enumeration", "points": 100},
    "FLAG{weak_admin_pass}": {"vuln_id": "7", "name": "Слабкий пароль адміна", "points": 100},
    "FLAG{xss_stored_review}": {"vuln_id": "8", "name": "Stored XSS (відгук)", "points": 150},
    "FLAG{xss_stored_name}": {"vuln_id": "9", "name": "Stored XSS (ім'я)", "points": 150},
    "FLAG{idor_chat}": {"vuln_id": "10", "name": "IDOR чат", "points": 150},
    "FLAG{idor_seller_email}": {"vuln_id": "11", "name": "IDOR продавець", "points": 150},
    "FLAG{jwt_role_change}": {"vuln_id": "12", "name": "JWT маніпуляція", "points": 150},
    "FLAG{csrf_email}": {"vuln_id": "13", "name": "CSRF зміна email", "points": 150},
    "FLAG{file_upload_rce}": {"vuln_id": "14", "name": "File upload RCE", "points": 150},
    "FLAG{mass_assign}": {"vuln_id": "15", "name": "Mass assignment", "points": 150},
    "FLAG{negative_qty}": {"vuln_id": "16", "name": "Business logic", "points": 150},
    "FLAG{blind_sqli}": {"vuln_id": "17", "name": "Blind SQL Injection", "points": 200},
    "FLAG{ssti_jinja}": {"vuln_id": "18", "name": "SSTI Jinja2", "points": 200},
    "FLAG{ssrf_preview}": {"vuln_id": "19", "name": "SSRF", "points": 200},
    "FLAG{path_traversal}": {"vuln_id": "20", "name": "Path traversal", "points": 200},
    "FLAG{second_order_sqli}": {"vuln_id": "21", "name": "Second-order SQLi", "points": 200},
    "FLAG{privesc_chain}": {"vuln_id": "22", "name": "Privilege escalation", "points": 200},
    "FLAG{race_condition}": {"vuln_id": "23", "name": "Race condition", "points": 200},
    "FLAG{sentry_leak}": {"vuln_id": "24", "name": "Sentry data exposure", "points": 200},
}


@flags_bp.route("/api/my-flags", methods=["GET"])
@jwt_required
def my_flags():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT vuln_id, flag_value, found_at FROM flags WHERE user_id = %s ORDER BY found_at",
        (g.user_id,),
    )
    rows = cur.fetchall()
    cur.close()

    found = []
    total_points = 0
    for row in rows:
        flag_value = row[1]
        meta = VALID_FLAGS.get(flag_value, {})
        points = meta.get("points", 0)
        total_points += points
        found.append({
            "vuln_id": row[0],
            "flag": flag_value,
            "name": meta.get("name", ""),
            "points": points,
            "found_at": row[2].strftime("%d.%m.%Y %H:%M") if row[2] else "",
        })

    return jsonify({
        "flags": found,
        "total_found": len(found),
        "total_flags": 24,
        "total_points": total_points,
    }), 200


@flags_bp.route("/api/flags/submit", methods=["POST"])
@jwt_required
def submit_flag():
    data = request.get_json() or {}
    flag_value = data.get("flag", "").strip()

    if flag_value not in VALID_FLAGS:
        return jsonify({"error": "Невірний флаг"}), 400

    meta = VALID_FLAGS[flag_value]
    vuln_id = meta["vuln_id"]

    db = get_db()
    cur = db.cursor()

    cur.execute(
        "SELECT id FROM flags WHERE user_id = %s AND flag_value = %s",
        (g.user_id, flag_value),
    )
    if cur.fetchone():
        cur.close()
        return jsonify({"error": "Цей флаг вже здано", "vuln_id": vuln_id}), 409

    cur.execute(
        "INSERT INTO flags (user_id, vuln_id, flag_value) VALUES (%s, %s, %s)",
        (g.user_id, vuln_id, flag_value),
    )
    cur.close()

    return jsonify({
        "ok": True,
        "points": meta["points"],
        "vuln_name": meta["name"],
        "vuln_id": vuln_id,
    }), 201

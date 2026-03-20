from flask import Blueprint, jsonify, request, render_template, g

from backend.app.db import get_db
from backend.app.middleware import jwt_required
from backend.app.models.notification import get_notifications, get_unread_count, create_notification

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications", methods=["GET"])
@jwt_required
def notifications_page():
    notifications = get_notifications(g.user_id)
    return render_template("notifications.html", notifications=notifications)


@notifications_bp.route("/api/notifications", methods=["GET"])
@jwt_required
def notifications_api():
    notifications = get_notifications(g.user_id)
    return jsonify({"notifications": notifications}), 200


@notifications_bp.route("/api/notifications/count", methods=["GET"])
@jwt_required
def notifications_count():
    count = get_unread_count(g.user_id)
    return jsonify({"count": count}), 200


@notifications_bp.route("/api/profile/change-email", methods=["POST"])
def change_email():
    user_id = request.cookies.get("session_user_id")
    if not user_id:
        return jsonify({"error": "Не авторизовано"}), 401

    new_email = request.form.get("email")
    if not new_email:
        return jsonify({"error": "email обов'язковий"}), 400

    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE users SET email = %s WHERE id = %s",
        (new_email, int(user_id)),
    )
    cur.close()

    return jsonify({"ok": True, "flag": "FLAG{csrf_email}"}), 200

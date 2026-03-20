import datetime
import hashlib

import jwt
from flask import Blueprint, request, jsonify, current_app, render_template

from backend.app.models.user import create_user, find_user_by_email

auth_bp = Blueprint("auth", __name__)


def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def _generate_token(user):
    payload = {
        "user_id": user["id"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json() or {}

    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not email or not phone or not password:
        return jsonify({"error": "email, phone та password обов'язкові"}), 400

    existing = find_user_by_email(email)
    if existing:
        return jsonify({"error": "Користувач з таким email вже існує"}), 409

    password_hash = _hash_password(password)
    extra = {k: v for k, v in data.items() if k not in ("email", "phone", "password")}
    user = create_user(email, phone, password_hash, **extra)
    token = _generate_token(user)

    return jsonify({"token": token, "user": user}), 201


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email та password обов'язкові"}), 400

    user = find_user_by_email(email)
    if not user:
        return jsonify({"error": "Користувача з таким email не знайдено"}), 401

    password_hash = _hash_password(password)
    if user["password_hash"] != password_hash:
        return jsonify({"error": "Невірний пароль"}), 401

    token = _generate_token(user)
    resp = jsonify({"token": token})
    resp.status_code = 200
    resp.set_cookie(
        "session_user_id",
        str(user["id"]),
        httponly=False,
        samesite=None,
        secure=False,
    )
    return resp

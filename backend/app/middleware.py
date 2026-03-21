from functools import wraps

import jwt
from flask import request, jsonify, redirect, current_app, g


def _wants_html():
    return "text/html" in request.headers.get("Accept", "")


def _deny(message):
    if _wants_html():
        return redirect("/login")
    return jsonify({"error": message}), 401


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _deny("Токен відсутній")

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return _deny("Токен протермінований")
        except jwt.InvalidTokenError:
            return _deny("Невалідний токен")

        g.user_id = payload["user_id"]
        g.user_role = payload.get("role", "buyer")
        return f(*args, **kwargs)

    return decorated

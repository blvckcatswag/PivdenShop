from functools import wraps

import jwt
from flask import request, jsonify, current_app, g


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Токен відсутній"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET_KEY"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Токен протермінований"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Невалідний токен"}), 401

        g.user_id = payload["user_id"]
        g.user_role = payload.get("role", "buyer")
        return f(*args, **kwargs)

    return decorated

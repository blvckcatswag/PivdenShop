import datetime
import jwt


def _make_token(app, user_id=1, role="buyer", expired=False):
    if expired:
        exp = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    else:
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    payload = {"user_id": user_id, "role": role, "exp": exp}
    return jwt.encode(payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")


class TestJwtMiddleware:
    def test_protected_route_without_token(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 401

    def test_protected_route_with_valid_token(self, client, app):
        reg = client.post("/register", json={
            "email": "jwt@example.com",
            "phone": "+380501234567",
            "password": "securePass1",
        })
        token = reg.get_json()["token"]
        resp = client.get("/profile", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 200

    def test_protected_route_with_expired_token(self, client, app):
        token = _make_token(app, expired=True)
        resp = client.get("/profile", headers={
            "Authorization": f"Bearer {token}",
        })
        assert resp.status_code == 401

    def test_protected_route_with_invalid_token(self, client):
        resp = client.get("/profile", headers={
            "Authorization": "Bearer invalid.token.here",
        })
        assert resp.status_code == 401

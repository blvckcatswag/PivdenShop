import json
import datetime
import jwt


class TestJwtRoleManipulation:
    def _register(self, client, email="attacker@test.com", phone="0501234567"):
        resp = client.post("/register", json={
            "email": email,
            "phone": phone,
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_jwt_role_manipulation(self, client, app):
        """Buyer should NOT be able to forge admin token — but can (JWT vuln #12)."""
        token = self._register(client)

        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["role"] == "buyer"

        forged_payload = {
            "user_id": payload["user_id"],
            "role": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        forged_token = jwt.encode(forged_payload, app.config["JWT_SECRET_KEY"], algorithm="HS256")

        resp = client.get("/admin", headers={"Authorization": f"Bearer {forged_token}"})

        assert resp.status_code == 403, "JWT role manipulation: forged admin token grants access to /admin"

    def test_jwt_none_algorithm(self, client, app):
        """None algorithm should be rejected."""
        token = self._register(client)
        payload = jwt.decode(token, options={"verify_signature": False})

        import base64
        header = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').rstrip(b'=').decode()
        body = base64.urlsafe_b64encode(
            json.dumps({"user_id": payload["user_id"], "role": "admin",
                         "exp": int((datetime.datetime.utcnow() + datetime.timedelta(hours=1)).timestamp())
                         }).encode()
        ).rstrip(b'=').decode()
        none_token = f"{header}.{body}."

        resp = client.get("/admin", headers={"Authorization": f"Bearer {none_token}"})
        assert resp.status_code == 401

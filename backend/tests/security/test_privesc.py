import json
import datetime
import jwt


class TestPrivescChain:
    def test_privesc_chain(self, client, app):
        """Full privilege escalation chain: buyer → seller → admin.
        Should NOT work — but does (#22)."""

        # Step 1: Register as buyer
        resp = client.post("/register", json={
            "email": "chain@test.com",
            "phone": "0509999999",
            "password": "password123",
        })
        data = json.loads(resp.data)
        token = data["token"]
        payload = jwt.decode(token, options={"verify_signature": False})
        assert payload["role"] == "buyer"

        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Become seller + mass assignment is_verified
        resp = client.post("/api/become-seller", headers=headers, json={
            "is_verified": True,
        })
        assert resp.status_code == 200

        # Step 3: Forge JWT with role=admin using dev secret
        forged_payload = {
            "user_id": payload["user_id"],
            "role": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        }
        forged_token = jwt.encode(
            forged_payload,
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )

        # Step 4: Access admin panel — should be 403 but is 200
        resp = client.get("/admin", headers={
            "Authorization": f"Bearer {forged_token}",
        })

        assert resp.status_code == 403, \
            "Privesc chain: buyer->seller->admin via JWT forgery grants admin access"
        assert b"FLAG{privesc_chain}" not in resp.data, \
            "Privesc chain flag should not be obtainable"

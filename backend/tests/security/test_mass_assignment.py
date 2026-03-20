import json


class TestMassAssignment:
    def test_register_with_is_verified_true(self, client):
        """Registration should NOT allow setting is_verified — but it does (mass assign vuln #15)."""
        resp = client.post("/register", json={
            "email": "hacker@test.com",
            "phone": "0501234567",
            "password": "password123",
            "is_verified": True,
        })
        assert resp.status_code == 201
        token = json.loads(resp.data)["token"]

        resp = client.get("/profile", headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        })
        data = json.loads(resp.data)
        assert data.get("is_verified") is not True, \
            "Mass assignment: is_verified=true accepted during registration"

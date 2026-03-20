import json


class TestProfileSsti:
    def _register(self, client):
        resp = client.post("/register", json={
            "email": "ssti@test.com",
            "phone": "0501234567",
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_profile_bio_ssti(self, client):
        """Bio field should NOT render Jinja2 templates — but it does (SSTI vuln #18)."""
        token = self._register(client)
        resp = client.put(
            "/api/profile",
            json={"bio": "{{7*7}}"},
            headers={"Authorization": f"Bearer {token}"},
        )
        data = json.loads(resp.data)
        assert data.get("bio") != "49", "SSTI: Jinja2 template executed in bio field"

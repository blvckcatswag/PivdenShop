import json


class TestFlagsApi:
    def _register(self, client):
        resp = client.post("/register", json={
            "email": "flagger@test.com",
            "phone": "0501234567",
            "password": "password123",
        })
        return json.loads(resp.data)["token"]

    def test_submit_valid_flag(self, client):
        token = self._register(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{sqli_search}",
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data["ok"] is True
        assert data["points"] == 100
        assert data["vuln_name"] == "SQL Injection"

    def test_submit_invalid_flag(self, client):
        token = self._register(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{not_real}",
        })
        assert resp.status_code == 400

    def test_submit_duplicate_flag(self, client):
        token = self._register(client)
        headers = {"Authorization": f"Bearer {token}"}

        client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{sqli_search}",
        })
        resp = client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{sqli_search}",
        })
        assert resp.status_code == 409

    def test_my_flags(self, client):
        token = self._register(client)
        headers = {"Authorization": f"Bearer {token}"}

        client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{sqli_search}",
        })
        client.post("/api/flags/submit", headers=headers, json={
            "flag": "FLAG{xss_reflected}",
        })

        resp = client.get("/api/my-flags", headers=headers)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["total_found"] == 2
        assert data["total_flags"] == 24
        assert data["total_points"] == 200

    def test_flags_requires_auth(self, client):
        resp = client.get("/api/my-flags")
        assert resp.status_code == 401

        resp = client.post("/api/flags/submit", json={"flag": "FLAG{sqli_search}"})
        assert resp.status_code == 401

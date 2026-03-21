import json


class TestSentryLeak:
    def test_debug_error_exposes_secrets(self, client):
        resp = client.get("/debug/error")
        assert resp.status_code == 500
        data = json.loads(resp.data)
        assert "DB_URL=" in data["error"]
        assert "JWT=" in data["error"]
        assert data["flag"] == "FLAG{sentry_leak}"

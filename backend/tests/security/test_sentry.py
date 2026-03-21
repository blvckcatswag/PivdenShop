import json


class TestSentryExposure:
    def test_debug_endpoint_should_not_leak_secrets(self, client):
        """Debug endpoint should NOT expose DB credentials and JWT secret — but does (#24)."""
        resp = client.get("/debug/error")
        data = json.loads(resp.data)

        assert "DB_URL=" not in data.get("error", ""), \
            "Debug endpoint leaks DATABASE_URL in error message"
        assert "JWT=" not in data.get("error", ""), \
            "Debug endpoint leaks JWT_SECRET_KEY in error message"
        assert data.get("flag") != "FLAG{sentry_leak}", \
            "Sentry leak flag should not be obtainable"

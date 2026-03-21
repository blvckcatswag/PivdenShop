class TestUnauthenticatedRedirect:
    """Browser requests to protected pages should redirect to /login."""

    def test_cart_redirects_browser_to_login(self, client):
        resp = client.get("/cart", headers={"Accept": "text/html"})
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_notifications_redirects_browser_to_login(self, client):
        resp = client.get("/notifications", headers={"Accept": "text/html"})
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_cart_returns_json_for_api(self, client):
        resp = client.get("/cart", headers={"Accept": "application/json"})
        assert resp.status_code == 401
        assert resp.get_json()["error"]

    def test_notifications_returns_json_for_api(self, client):
        resp = client.get(
            "/notifications", headers={"Accept": "application/json"}
        )
        assert resp.status_code == 401
        assert resp.get_json()["error"]

    def test_profile_redirects_browser_to_login(self, client):
        resp = client.get("/profile", headers={"Accept": "text/html"})
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_checkout_redirects_browser_to_login(self, client):
        resp = client.get("/checkout", headers={"Accept": "text/html"})
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

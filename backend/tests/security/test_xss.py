class TestReflectedXss:
    def test_search_reflected_xss(self, client):
        payload = "<script>alert(1)</script>"
        resp = client.get(f"/search?q={payload}")

        assert resp.status_code == 200
        assert payload.encode() not in resp.data, (
            "Reflected XSS: search parameter is rendered without escaping in HTML response"
        )

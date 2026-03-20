import base64


class TestApiDocs:
    def test_api_docs_requires_auth(self, client):
        resp = client.get("/api/docs/")
        assert resp.status_code == 401

    def test_api_docs_accessible_with_auth(self, client, app):
        username = app.config["API_DOCS_USERNAME"]
        password = app.config["API_DOCS_PASSWORD"]
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        resp = client.get("/api/docs/", headers={
            "Authorization": f"Basic {credentials}",
        })
        assert resp.status_code == 200

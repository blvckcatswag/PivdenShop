class TestDirectoryListing:
    def test_uploads_listing_returns_200(self, client):
        resp = client.get("/static/uploads/")
        assert resp.status_code == 200

    def test_uploads_listing_shows_files(self, client):
        resp = client.get("/static/uploads/")
        assert b"test_document.pdf" in resp.data
        assert b"user_42_avatar.jpg" in resp.data
        assert b"invoice_2024.xlsx" in resp.data

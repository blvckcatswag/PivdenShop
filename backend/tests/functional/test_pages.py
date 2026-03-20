class TestHomePage:
    def test_home_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_contains_products(self, client, app):
        from backend.seed import run_seed
        with app.app_context():
            run_seed()
        resp = client.get("/")
        assert b"product-card" in resp.data


class TestProductsPage:
    def test_products_page_returns_200(self, client):
        resp = client.get("/products")
        assert resp.status_code == 200

    def test_products_page_shows_grid(self, client, app):
        from backend.seed import run_seed
        with app.app_context():
            run_seed()
        resp = client.get("/products")
        assert b"products-grid" in resp.data

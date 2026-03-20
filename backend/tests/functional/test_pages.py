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


class TestRegisterPage:
    def test_register_page_returns_200(self, client):
        resp = client.get("/register")
        assert resp.status_code == 200

    def test_register_page_has_form(self, client):
        resp = client.get("/register")
        assert b"<form" in resp.data
        assert b"email" in resp.data
        assert b"password" in resp.data
        assert b"phone" in resp.data


class TestLoginPage:
    def test_login_page_returns_200(self, client):
        resp = client.get("/login")
        assert resp.status_code == 200

    def test_login_page_has_form(self, client):
        resp = client.get("/login")
        assert b"<form" in resp.data
        assert b"email" in resp.data
        assert b"password" in resp.data

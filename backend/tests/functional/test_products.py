class TestProducts:
    def test_products_empty(self, client):
        resp = client.get("/products")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "products" in data
        assert isinstance(data["products"], list)

    def test_products_search(self, client):
        resp = client.get("/products?search=test")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "products" in data

class TestSearchSqli:
    def test_search_sqli(self, client, app):
        resp = client.get("/products?search=' OR 1=1--", headers={"Accept": "application/json"})
        data = resp.get_json()

        resp_normal = client.get("/products?search=nonexistent_product_xyz", headers={"Accept": "application/json"})
        data_normal = resp_normal.get_json()

        assert len(data["products"]) > len(data_normal["products"]), (
            "SQLi payload ' OR 1=1-- should return more results than a normal search"
        )

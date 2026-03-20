import json


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/register", json={
            "email": "user@example.com",
            "phone": "+380501234567",
            "password": "securePass1",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert data["user"]["email"] == "user@example.com"

    def test_register_duplicate_email(self, client):
        payload = {
            "email": "dup@example.com",
            "phone": "+380501234567",
            "password": "securePass1",
        }
        client.post("/register", json=payload)
        resp = client.post("/register", json=payload)
        assert resp.status_code == 409
        data = resp.get_json()
        assert "error" in data

    def test_register_missing_fields(self, client):
        resp = client.post("/register", json={"email": "no@fields.com"})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data


class TestLogin:
    def _create_user(self, client):
        client.post("/register", json={
            "email": "login@example.com",
            "phone": "+380501234567",
            "password": "correctPass1",
        })

    def test_login_success(self, client):
        self._create_user(client)
        resp = client.post("/login", json={
            "email": "login@example.com",
            "password": "correctPass1",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data

    def test_login_wrong_password(self, client):
        self._create_user(client)
        resp = client.post("/login", json={
            "email": "login@example.com",
            "password": "wrongPass",
        })
        assert resp.status_code == 401

    def test_login_wrong_email(self, client):
        resp = client.post("/login", json={
            "email": "nobody@example.com",
            "password": "whatever",
        })
        assert resp.status_code == 401

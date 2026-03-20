class TestUsernameEnumeration:
    """Vuln #6: login should return identical messages for wrong email and wrong password.
    This test stays RED — the app intentionally leaks which field is wrong."""

    def _create_user(self, client):
        client.post("/register", json={
            "email": "enum@example.com",
            "phone": "+380501234567",
            "password": "correctPass1",
        })

    def test_login_username_enumeration(self, client):
        self._create_user(client)

        resp_wrong_email = client.post("/login", json={
            "email": "nonexistent@example.com",
            "password": "whatever",
        })

        resp_wrong_pass = client.post("/login", json={
            "email": "enum@example.com",
            "password": "wrongPassword",
        })

        msg_wrong_email = resp_wrong_email.get_json().get("error", "")
        msg_wrong_pass = resp_wrong_pass.get_json().get("error", "")

        assert msg_wrong_email == msg_wrong_pass, (
            f"Username enumeration: different error messages "
            f"reveal whether email exists. "
            f"Wrong email: '{msg_wrong_email}' vs "
            f"Wrong password: '{msg_wrong_pass}'"
        )

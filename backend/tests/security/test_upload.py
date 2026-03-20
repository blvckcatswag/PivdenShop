import io
import json
import datetime
import jwt


class TestFileUpload:
    def _register_seller(self, client, app):
        resp = client.post("/register", json={
            "email": "seller@upload.com",
            "phone": "0501234567",
            "password": "password123",
        })
        token = json.loads(resp.data)["token"]
        payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])

        from backend.app.db import get_db
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("UPDATE users SET is_seller = true WHERE id = %s", (payload["user_id"],))
            cur.close()

        seller_token = jwt.encode(
            {"user_id": payload["user_id"], "role": "seller",
             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config["JWT_SECRET_KEY"],
            algorithm="HS256",
        )
        return seller_token

    def test_file_upload_accepts_executable(self, client, app):
        """Server should NOT accept .php files — but it does (file upload vuln #14)."""
        token = self._register_seller(client, app)

        data = {
            "file": (io.BytesIO(b"<?php system($_GET['cmd']); ?>"), "shell.php", "image/jpeg"),
        }
        resp = client.post(
            "/api/upload/avatar",
            data=data,
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {token}"},
        )
        result = json.loads(resp.data)

        assert resp.status_code != 200 or "shell.php" not in result.get("url", ""), \
            "Executable file accepted without validation"

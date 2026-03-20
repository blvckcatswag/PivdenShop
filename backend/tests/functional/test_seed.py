import pytest
from backend.app.db import get_db


@pytest.fixture(autouse=True)
def _run_seed(app):
    from backend.seed import run_seed
    with app.app_context():
        run_seed()
    yield


class TestSeedData:
    def test_seed_creates_sellers(self, app):
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM users WHERE is_seller = TRUE")
            count = cur.fetchone()[0]
            cur.close()
        assert count >= 5

    def test_seed_creates_products(self, app):
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM products")
            count = cur.fetchone()[0]
            cur.close()
        assert count >= 50

    def test_seed_creates_orders(self, app):
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM orders")
            count = cur.fetchone()[0]
            cur.close()
        assert count >= 3

    def test_seed_creates_chats_with_card_number(self, app):
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute("SELECT COUNT(*) FROM chats")
            chat_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM messages WHERE text LIKE '%4242424242424242%'")
            card_msg_count = cur.fetchone()[0]
            cur.close()
        assert chat_count >= 1
        assert card_msg_count >= 1

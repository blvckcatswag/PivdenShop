from backend.app.db import get_db, close_db, init_db


def test_db_connection(app):
    with app.app_context():
        conn = get_db()
        assert conn is not None
        assert conn.closed == 0
        close_db()


def test_db_returns_cursor(app):
    with app.app_context():
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result == (1,)
        cur.close()
        close_db()


def test_db_connection_pool(app):
    with app.app_context():
        conn1 = get_db()
        assert conn1 is not None
        assert conn1.closed == 0
        close_db()

    with app.app_context():
        conn2 = get_db()
        assert conn2 is not None
        assert conn2.closed == 0
        close_db()

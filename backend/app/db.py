import os

import psycopg2
from psycopg2 import pool
from flask import g, current_app

_pool = None


def _get_pool():
    global _pool
    if _pool is None or _pool.closed:
        db_url = current_app.config["DATABASE_URL"]
        _pool = pool.SimpleConnectionPool(1, 10, db_url)
    return _pool


def get_db():
    if "db" not in g:
        g.db = _get_pool().getconn()
        g.db.autocommit = True
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        _get_pool().putconn(db)


def init_db(app=None):
    a = app or current_app._get_current_object()
    db_url = a.config.get("DATABASE_URL", "")
    print(f"[DB] Connecting to: {db_url[:30]}...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        schema_path = os.path.join(
            os.path.dirname(__file__), "schema.sql")
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()
        cur.execute(sql)
        cur.close()
        conn.close()
        print("[DB] Schema initialized successfully")
    except Exception as e:
        print(f"[DB] WARNING: Could not init DB: {e}")
        print("[DB] App will start without DB connection")
        return

import os
import pytest
import psycopg2

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:PostgreSQL_SuperAdmin_Password1337!@localhost:5432/pivdenshop_test",
)

from backend.app import create_app


@pytest.fixture(scope="session")
def _create_test_db():
    db_url = os.environ["DATABASE_URL"]
    base_url = db_url.rsplit("/", 1)[0]
    test_db = db_url.rsplit("/", 1)[1]

    conn = psycopg2.connect(base_url + "/postgres")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (test_db,)
    )
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{test_db}"')
    cur.close()
    conn.close()


@pytest.fixture(scope="session")
def app(_create_test_db):
    app = create_app(testing=True)
    yield app


@pytest.fixture(scope="session")
def _init_schema(app):
    db_url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100) DEFAULT '',
            role VARCHAR(20) DEFAULT 'buyer',
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    cur.close()
    conn.close()


@pytest.fixture(autouse=True)
def _clean_users(_init_schema):
    yield
    db_url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("DELETE FROM users")
    cur.close()
    conn.close()


@pytest.fixture
def client(app):
    return app.test_client()

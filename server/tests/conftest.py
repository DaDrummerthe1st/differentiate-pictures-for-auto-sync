import os

import psycopg
import pytest
import redis

from app.db import ensure_schema

TEST_DSN = dict(
    host=os.environ.get("TEST_POSTGRES_HOST", "127.0.0.1"),
    port=os.environ.get("TEST_POSTGRES_PORT", "5433"),
    dbname=os.environ.get("TEST_POSTGRES_DB", "photo_server_test"),
    user=os.environ.get("TEST_POSTGRES_USER", "photo_server"),
    password=os.environ.get("TEST_POSTGRES_PASSWORD", "test"),
)

TEST_REDIS_PORT = os.environ.get("TEST_REDIS_PORT", "6380")
TEST_REDIS_PASSWORD = os.environ.get("TEST_REDIS_PASSWORD", "test")
TEST_REDIS_URL = f"redis://:{TEST_REDIS_PASSWORD}@127.0.0.1:{TEST_REDIS_PORT}/0"

# app.main validates its required POSTGRES_*/REDIS_URL/JWT_SECRET_KEY env
# vars at import time (fail-fast startup, TODO.md 0.4) — point them at the
# disposable test containers so `from app.main import app` succeeds
# during collection.
os.environ.setdefault("POSTGRES_HOST", TEST_DSN["host"])
os.environ.setdefault("POSTGRES_PORT", str(TEST_DSN["port"]))
os.environ.setdefault("POSTGRES_DB", TEST_DSN["dbname"])
os.environ.setdefault("POSTGRES_USER", TEST_DSN["user"])
os.environ.setdefault("POSTGRES_PASSWORD", TEST_DSN["password"])
os.environ.setdefault("REDIS_URL", TEST_REDIS_URL)
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-chars")


@pytest.fixture(scope="session", autouse=True)
def _schema():
    conn = psycopg.connect(**TEST_DSN, autocommit=True)
    ensure_schema(conn)
    conn.close()


@pytest.fixture()
def db_connection():
    conn = psycopg.connect(**TEST_DSN)
    yield conn
    conn.rollback()
    conn.close()


@pytest.fixture()
def redis_client():
    client = redis.Redis.from_url(TEST_REDIS_URL)
    client.flushdb()
    yield client
    client.flushdb()
    client.close()

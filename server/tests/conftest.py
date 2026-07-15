import os

import psycopg
import pytest

from app.db import ensure_schema

TEST_DSN = dict(
    host=os.environ.get("TEST_POSTGRES_HOST", "127.0.0.1"),
    port=os.environ.get("TEST_POSTGRES_PORT", "5433"),
    dbname=os.environ.get("TEST_POSTGRES_DB", "photo_server_test"),
    user=os.environ.get("TEST_POSTGRES_USER", "photo_server"),
    password=os.environ.get("TEST_POSTGRES_PASSWORD", "test"),
)


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

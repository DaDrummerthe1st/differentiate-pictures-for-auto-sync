import psycopg

from app.config import load_db_config


def get_connection() -> psycopg.Connection:
    config = load_db_config()
    return psycopg.connect(
        host=config["POSTGRES_HOST"],
        port=config["POSTGRES_PORT"],
        dbname=config["POSTGRES_DB"],
        user=config["POSTGRES_USER"],
        password=config["POSTGRES_PASSWORD"],
    )


def ensure_schema(conn: psycopg.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id BIGSERIAL PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )

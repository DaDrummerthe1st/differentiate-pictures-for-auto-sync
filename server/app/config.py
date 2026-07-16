import os

REQUIRED_DB_ENV_VARS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


class MissingConfigError(RuntimeError):
    pass


def load_db_config() -> dict[str, str]:
    missing = [name for name in REQUIRED_DB_ENV_VARS if name not in os.environ]
    if missing:
        raise MissingConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}"
        )
    return {name: os.environ[name] for name in REQUIRED_DB_ENV_VARS}

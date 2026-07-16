import os

REQUIRED_DB_ENV_VARS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)

REQUIRED_AUTH_ENV_VARS = (
    "REDIS_URL",
    "JWT_SECRET_KEY",
)


class MissingConfigError(RuntimeError):
    pass


def _load(required: tuple[str, ...]) -> dict[str, str]:
    missing = [name for name in required if name not in os.environ]
    if missing:
        raise MissingConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}"
        )
    return {name: os.environ[name] for name in required}


def load_db_config() -> dict[str, str]:
    return _load(REQUIRED_DB_ENV_VARS)


MIN_JWT_SECRET_KEY_LENGTH = 32


def load_auth_config() -> dict[str, str]:
    config = _load(REQUIRED_AUTH_ENV_VARS)
    if len(config["JWT_SECRET_KEY"]) < MIN_JWT_SECRET_KEY_LENGTH:
        raise MissingConfigError(
            f"JWT_SECRET_KEY must be at least {MIN_JWT_SECRET_KEY_LENGTH} characters"
        )
    return config

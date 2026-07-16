import importlib

import pytest

from app.config import MissingConfigError, load_auth_config, load_db_config

REQUIRED_VARS = {
    "POSTGRES_HOST": "db.example.test",
    "POSTGRES_PORT": "5432",
    "POSTGRES_DB": "photo_server",
    "POSTGRES_USER": "photo_server",
    "POSTGRES_PASSWORD": "secret",
}

REQUIRED_AUTH_VARS = {
    "REDIS_URL": "redis://:secret@redis.example.test:6379/0",
    "JWT_SECRET_KEY": "a" * 32,
}


def _set_all(monkeypatch):
    for name, value in REQUIRED_VARS.items():
        monkeypatch.setenv(name, value)


def _set_all_auth(monkeypatch):
    for name, value in REQUIRED_AUTH_VARS.items():
        monkeypatch.setenv(name, value)


def test_load_db_config_returns_all_required_values(monkeypatch):
    _set_all(monkeypatch)

    assert load_db_config() == REQUIRED_VARS


@pytest.mark.parametrize("missing_var", sorted(REQUIRED_VARS))
def test_load_db_config_fails_fast_when_a_required_var_is_missing(monkeypatch, missing_var):
    _set_all(monkeypatch)
    monkeypatch.delenv(missing_var)

    with pytest.raises(MissingConfigError):
        load_db_config()


def test_load_auth_config_returns_all_required_values(monkeypatch):
    _set_all_auth(monkeypatch)

    assert load_auth_config() == REQUIRED_AUTH_VARS


@pytest.mark.parametrize("missing_var", sorted(REQUIRED_AUTH_VARS))
def test_load_auth_config_fails_fast_when_a_required_var_is_missing(monkeypatch, missing_var):
    _set_all_auth(monkeypatch)
    monkeypatch.delenv(missing_var)

    with pytest.raises(MissingConfigError):
        load_auth_config()


def test_importing_app_main_fails_immediately_when_config_is_missing(monkeypatch):
    _set_all(monkeypatch)
    _set_all_auth(monkeypatch)
    monkeypatch.delenv("POSTGRES_PASSWORD")

    import app.main

    with pytest.raises(MissingConfigError):
        importlib.reload(app.main)

    # restore a valid environment so later test modules can import app.main cleanly
    monkeypatch.setenv("POSTGRES_PASSWORD", REQUIRED_VARS["POSTGRES_PASSWORD"])
    importlib.reload(app.main)

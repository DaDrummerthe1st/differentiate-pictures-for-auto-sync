from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_startup_initializes_database_schema():
    mock_conn = MagicMock()
    with (
        patch("app.main.get_connection", return_value=mock_conn) as mock_get_connection,
        patch("app.main.ensure_schema") as mock_ensure_schema,
    ):
        with TestClient(app):
            pass

    mock_get_connection.assert_called_once()
    mock_ensure_schema.assert_called_once_with(mock_conn)

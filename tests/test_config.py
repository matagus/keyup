"""Tests for KeyUp! config module."""

from unittest.mock import patch

from keyup.cli.config import init_environ


class TestInitEnviron:
    """Tests for init_environ function."""

    @patch("dotenv.load_dotenv")
    @patch("dotenv.dotenv_values")
    def test_init_environ_loads_env(self, mock_values, mock_load):
        """Test that init_environ loads environment variables."""
        mock_values.return_value = {"TOKEN": "test-token"}
        result = init_environ()
        mock_load.assert_called_once_with(".env")
        assert result == {"TOKEN": "test-token"}

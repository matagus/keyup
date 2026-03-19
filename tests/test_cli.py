"""Tests for KeyUp! CLI module."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call

from keyup.cli.main import app, list_tasks


class TestApp:
    """Tests for the CLI app."""

    def test_app_creation(self):
        """Test that app is created with correct name."""
        assert "keyup" in app.name
        assert "console-based client for ClickUp" in app.help

    def test_app_help(self, capsys):
        """Test that --help works."""
        app(["--help"])
        captured = capsys.readouterr()
        assert "Team ID" in captured.out
        assert "Space ID" in captured.out
        assert "Project ID" in captured.out
        assert "List ID" in captured.out


class TestListTasks:
    """Tests for the list_tasks command."""

    @patch("keyup.cli.main.render_list")
    @patch("keyup.cli.main.get_list_for")
    @patch("keyup.cli.main.get_project_for")
    @patch("keyup.cli.main.get_space_for")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_list_tasks_with_all_params(self, mock_environ, mock_clickup_class,
                                         mock_get_team, mock_get_space_for,
                                         mock_get_project_for, mock_get_list_for,
                                         mock_render_list, capsys):
        """Test list_tasks with all parameters provided."""
        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_team = Mock()
        mock_space = Mock()
        mock_project = Mock()
        mock_list = Mock()

        mock_get_team.return_value = mock_team
        mock_get_space_for.return_value = mock_space
        mock_get_project_for.return_value = mock_project
        mock_get_list_for.return_value = mock_list

        list_tasks(
            team="team-123",
            space="space-456",
            project="project-789",
            list_id="list-000"
        )

        mock_environ.assert_called_once()
        mock_clickup_class.assert_called_once_with("test-token")
        mock_get_team.assert_called()
        mock_get_space_for.assert_called()
        mock_get_project_for.assert_called()
        mock_get_list_for.assert_called()
        mock_render_list.assert_called_once_with(mock_list, mock_team)

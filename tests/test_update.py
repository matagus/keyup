"""Tests for QuickUp! update command."""

from unittest.mock import patch

from quickup.cli.renderer import render_task_update


class TestRenderTaskUpdate:
    """Tests for render_task_update function."""

    @patch("builtins.print")
    def test_render_task_update_basic(self, mock_print):
        """Test render_task_update shows update confirmation."""
        render_task_update("task-123", "To Do", "In Progress")

        # Verify print was called multiple times
        assert mock_print.called

    @patch("builtins.print")
    def test_render_task_update_shows_task_id(self, mock_print):
        """Test render_task_update shows task ID."""
        render_task_update("task-456", "To Do", "Done")

        printed_args = [str(arg) for call in mock_print.call_args_list for arg in call[0]]
        assert any("task-456" in arg for arg in printed_args)

    @patch("builtins.print")
    def test_render_task_update_shows_status_transition(self, mock_print):
        """Test render_task_update shows old -> new status."""
        render_task_update("task-789", "In Progress", "Done")

        printed_args = [str(arg) for call in mock_print.call_args_list for arg in call[0]]
        # Check that both old and new status are mentioned
        assert any("In Progress" in arg for arg in printed_args)
        assert any("Done" in arg for arg in printed_args)

    @patch("builtins.print")
    def test_render_task_update_success_message(self, mock_print):
        """Test render_task_update shows success message."""
        render_task_update("task-123", "To Do", "In Progress")

        printed_args = [str(arg) for call in mock_print.call_args_list for arg in call[0]]
        assert any("successfully" in arg.lower() for arg in printed_args)

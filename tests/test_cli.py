"""Tests for KeyUp! CLI module."""

from unittest.mock import Mock, patch

from keyup.cli.main import app, list_tasks, update_task, show_task


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
    def test_list_tasks_with_all_params(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_get_space_for,
        mock_get_project_for,
        mock_get_list_for,
        mock_render_list,
        capsys,
    ):
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

        list_tasks(team="team-123", space="space-456", project="project-789", list_id="list-000")

        mock_environ.assert_called_once()
        mock_clickup_class.assert_called_once_with("test-token")
        mock_get_team.assert_called()
        mock_get_space_for.assert_called()
        mock_get_project_for.assert_called()
        mock_get_list_for.assert_called()
        mock_render_list.assert_called_once_with(
            mock_list, mock_team, no_cache=False, assignee=None, priority=None, due_before=None, group_by="status",
            team="team-123", space="space-456", project="project-789", list_id="list-000"
        )


class TestUpdateTask:
    """Tests for the update_task command."""

    @patch("keyup.cli.main.render_task_update")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_with_team_id(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_update,
        capsys,
    ):
        """Test update_task with explicit team ID."""
        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_team = Mock(id="team-123")
        mock_get_team.return_value = mock_team

        mock_task = Mock()
        mock_task.id = "task-86b8z0dn3"
        mock_task.status.status = "To Do"

        mock_clickup._get_all_tasks.return_value = [mock_task]

        update_task(task_id="task-86b8z0dn3", status="In Progress", team="team-123")

        mock_get_team.assert_called()
        mock_render_task_update.assert_called_once_with("task-86b8z0dn3", "To Do", "In Progress")

    @patch("keyup.cli.main.render_task_update")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_without_team_uses_first_team(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_update,
        capsys,
    ):
        """Test update_task without team ID uses first team."""
        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_team = Mock(id="team-456")
        mock_clickup.teams = [mock_team]
        mock_get_team.return_value = None

        mock_task = Mock()
        mock_task.id = "task-123"
        mock_task.status.status = "To Do"

        mock_clickup._get_all_tasks.return_value = [mock_task]

        update_task(task_id="task-123", status="Done")

        mock_render_task_update.assert_called_once_with("task-123", "To Do", "Done")

    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_not_found(
        self,
        mock_environ,
        mock_clickup_class,
        capsys,
    ):
        """Test update_task raises error when task not found."""
        from keyup.cli.exceptions import ClickupyError

        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = []

        import pytest
        with pytest.raises(ClickupyError, match="Task .* not found"):
            update_task(task_id="nonexistent", status="Done")


class TestShowTask:
    """Tests for the show_task command."""

    @patch("keyup.cli.main.render_task_detail")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_with_team_id(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_detail,
        capsys,
    ):
        """Test show_task with explicit team ID."""
        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_team = Mock(id="team-123")
        mock_get_team.return_value = mock_team

        mock_task = Mock()
        mock_task.id = "task-86b8z0dn3"

        mock_clickup._get_all_tasks.return_value = [mock_task]

        show_task(task_id="task-86b8z0dn3", team="team-123")

        mock_get_team.assert_called()
        mock_render_task_detail.assert_called_once_with(mock_task)

    @patch("keyup.cli.main.render_task_detail")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_without_team_uses_first_team(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_detail,
        capsys,
    ):
        """Test show_task without team ID uses first team."""
        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_team = Mock(id="team-456")
        mock_clickup.teams = [mock_team]
        mock_get_team.return_value = None

        mock_task = Mock()
        mock_task.id = "task-123"

        mock_clickup._get_all_tasks.return_value = [mock_task]

        show_task(task_id="task-123")

        mock_render_task_detail.assert_called_once_with(mock_task)

    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_not_found(
        self,
        mock_environ,
        mock_clickup_class,
        capsys,
    ):
        """Test show_task raises error when task not found."""
        from keyup.cli.exceptions import ClickupyError

        mock_environ.return_value = {"TOKEN": "test-token"}
        mock_clickup = Mock()
        mock_clickup_class.return_value = mock_clickup

        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = []

        import pytest
        with pytest.raises(ClickupyError, match="Task .* not found"):
            show_task(task_id="nonexistent")


class TestUpdateTask:
    """Tests for the update_task command."""

    @patch("keyup.cli.main.render_task_update")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_basic(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_update,
        capsys,
    ):
        """Test update_task with required parameters."""
        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_clickup = Mock()
        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="task-86b8z0dn3", status=Mock(status="To Do")),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = None

        update_task(task_id="task-86b8z0dn3", status="In Progress")

        mock_environ.assert_called_once()
        mock_clickup_class.assert_called_once_with("test-token")
        mock_get_team.assert_called_once()
        mock_render_task_update.assert_called_once_with("task-86b8z0dn3", "To Do", "In Progress")

    @patch("keyup.cli.main.render_task_update")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_with_team(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_update,
        capsys,
    ):
        """Test update_task with team parameter."""
        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_team = Mock(id="team-456")
        mock_clickup = Mock()
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="task-86b8z0dn3", status=Mock(status="To Do")),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = mock_team

        update_task(task_id="task-86b8z0dn3", status="In Progress", team="team-456")

        mock_get_team.assert_called_once()
        mock_render_task_update.assert_called_once_with("task-86b8z0dn3", "To Do", "In Progress")

    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_update_task_not_found(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
    ):
        """Test update_task raises error when task not found."""
        from keyup.cli.exceptions import ClickupyError

        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_clickup = Mock()
        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="other-task"),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = None

        import pytest
        with pytest.raises(ClickupyError, match="Task task-not-found not found"):
            update_task(task_id="task-not-found", status="In Progress")


class TestShowTask:
    """Tests for the show_task command."""

    @patch("keyup.cli.main.render_task_detail")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_basic(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_detail,
        capsys,
    ):
        """Test show_task with required parameters."""
        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_clickup = Mock()
        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="task-123"),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = None

        show_task(task_id="task-123")

        mock_environ.assert_called_once()
        mock_clickup_class.assert_called_once_with("test-token")
        mock_get_team.assert_called_once()
        mock_render_task_detail.assert_called_once()

    @patch("keyup.cli.main.render_task_detail")
    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_with_team(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
        mock_render_task_detail,
        capsys,
    ):
        """Test show_task with team parameter."""
        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_team = Mock(id="team-456")
        mock_clickup = Mock()
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="task-123"),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = mock_team

        show_task(task_id="task-123", team="team-456")

        mock_get_team.assert_called_once()
        mock_render_task_detail.assert_called_once()

    @patch("keyup.cli.main.get_team")
    @patch("keyup.cli.main.ClickUp")
    @patch("keyup.cli.main.init_environ")
    def test_show_task_not_found(
        self,
        mock_environ,
        mock_clickup_class,
        mock_get_team,
    ):
        """Test show_task raises error when task not found."""
        from keyup.cli.exceptions import ClickupyError

        mock_environ.return_value = {"TOKEN": "test-token"}

        mock_clickup = Mock()
        mock_clickup.teams = [Mock(id="team-123")]
        mock_clickup._get_all_tasks.return_value = [
            Mock(id="other-task"),
        ]
        mock_clickup_class.return_value = mock_clickup

        mock_get_team.return_value = None

        import pytest
        with pytest.raises(ClickupyError, match="Task task-not-found not found"):
            show_task(task_id="task-not-found")

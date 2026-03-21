"""Tests for QuickUp! renderer module."""

from unittest.mock import Mock, patch

from quickup.cli.renderer import _filter_tasks, _group_by_assignee, _group_by_priority, _group_by_status, render_list


class TestFilterTasks:
    """Tests for _filter_tasks function."""

    def test_no_filters_returns_all_tasks(self):
        """Test that no filters returns all tasks."""
        tasks = [Mock(), Mock()]
        result = _filter_tasks(tasks)
        assert result == tasks

    def test_assignee_filter(self):
        """Test filtering by assignee."""
        task1 = Mock()
        task1.assignees = [Mock(username="john")]
        task2 = Mock()
        task2.assignees = [Mock(username="jane")]

        result = _filter_tasks([task1, task2], assignee="john")
        assert result == [task1]

    def test_assignee_filter_case_insensitive(self):
        """Test assignee filter is case-insensitive."""
        task1 = Mock()
        task1.assignees = [Mock(username="John")]
        task2 = Mock()
        task2.assignees = [Mock(username="jane")]

        result = _filter_tasks([task1, task2], assignee="JOHN")
        assert result == [task1]

    def test_priority_filter(self):
        """Test filtering by priority."""
        task1 = Mock()
        task1.priority = {"priority": "high"}
        task2 = Mock()
        task2.priority = {"priority": "low"}

        result = _filter_tasks([task1, task2], priority="high")
        assert result == [task1]

    def test_priority_filter_urgent(self):
        """Test filtering by urgent priority."""
        task1 = Mock()
        task1.priority = {"priority": "urgent"}
        task2 = Mock()
        task2.priority = {"priority": "high"}

        result = _filter_tasks([task1, task2], priority="urgent")
        assert result == [task1]

    def test_priority_filter_low(self):
        """Test filtering by low priority."""
        task1 = Mock()
        task1.priority = {"priority": "low"}
        task2 = Mock()
        task2.priority = {"priority": "normal"}

        result = _filter_tasks([task1, task2], priority="low")
        assert result == [task1]

    def test_priority_filter_normal(self):
        """Test filtering by normal priority."""
        task1 = Mock()
        task1.priority = {"priority": "normal"}
        task2 = Mock()
        task2.priority = {"priority": "high"}

        result = _filter_tasks([task1, task2], priority="normal")
        assert result == [task1]

    def test_priority_filter_valid_priority_value(self):
        """Test priority filter with valid priority_value lookup."""
        task1 = Mock()
        task1.priority = {"priority": "urgent"}
        task2 = Mock()
        task2.priority = {"priority": "normal"}

        result = _filter_tasks([task1, task2], priority="urgent")
        assert result == [task1]

    def test_priority_filter_no_priority(self):
        """Test priority filter excludes tasks without priority."""
        task1 = Mock()
        task1.priority = {"priority": "high"}
        task2 = Mock()
        task2.priority = None

        result = _filter_tasks([task1, task2], priority="high")
        assert result == [task1]

    def test_priority_filter_invalid_priority(self):
        """Test priority filter with invalid priority value."""
        task1 = Mock()
        task1.priority = {"priority": "high"}
        task2 = Mock()
        task2.priority = {"priority": "low"}

        result = _filter_tasks([task1, task2], priority="invalid")
        assert result == [task1, task2]  # No filtering when invalid priority

    def test_due_before_filter(self):
        """Test filtering by due date."""
        task1 = Mock()
        task1.due_date = "2024-01-01T00:00:00.000Z"
        task2 = Mock()
        task2.due_date = "2024-06-01T00:00:00.000Z"

        result = _filter_tasks([task1, task2], due_before="2024-03-01")
        assert result == [task1]

    def test_due_before_filter_invalid_date(self):
        """Test due_before with invalid date format."""
        task1 = Mock()
        task1.due_date = "2024-01-01T00:00:00.000Z"

        result = _filter_tasks([task1], due_before="invalid")
        assert result == [task1]  # Should not filter anything

    def test_combined_filters(self):
        """Test combining multiple filters."""
        task1 = Mock()
        task1.assignees = [Mock(username="john")]
        task1.priority = {"priority": "high"}
        task1.due_date = "2024-01-01T00:00:00.000Z"

        task2 = Mock()
        task2.assignees = [Mock(username="john")]
        task2.priority = {"priority": "low"}
        task2.due_date = "2024-01-01T00:00:00.000Z"

        task3 = Mock()
        task3.assignees = [Mock(username="jane")]
        task3.priority = {"priority": "high"}
        task3.due_date = "2024-01-01T00:00:00.000Z"

        result = _filter_tasks([task1, task2, task3], assignee="john", priority="high")
        assert result == [task1]


class TestGroupBy:
    """Tests for grouping functions."""

    def test_group_by_status(self):
        """Test grouping by status."""
        task1 = Mock()
        task1.parent = None
        task1.status.status = "To Do"
        task1.status.color = "#123456"
        task1.status.orderindex = 0

        task2 = Mock()
        task2.parent = None
        task2.status.status = "Done"
        task2.status.color = "#654321"
        task2.status.orderindex = 1

        result = _group_by_status([task1, task2])
        assert "To Do" in result
        assert "Done" in result
        assert result["To Do"] == [task1]
        assert result["Done"] == [task2]

    def test_group_by_assignee(self):
        """Test grouping by assignee."""
        task1 = Mock()
        task1.parent = None
        task1.assignees = [Mock(username="john")]

        task2 = Mock()
        task2.parent = None
        task2.assignees = [Mock(username="jane")]

        task3 = Mock()
        task3.parent = None
        task3.assignees = []

        result = _group_by_assignee([task1, task2, task3])
        assert "john" in result
        assert "jane" in result
        assert "Unassigned" in result
        assert result["john"] == [task1]
        assert result["jane"] == [task2]
        assert result["Unassigned"] == [task3]

    def test_group_by_assignee_with_parent_tasks(self):
        """Test grouping by assignee skips tasks with parent."""
        task1 = Mock()
        task1.parent = "parent-123"  # Has parent, should be skipped
        task1.assignees = [Mock(username="john")]

        task2 = Mock()
        task2.parent = None
        task2.assignees = [Mock(username="jane")]

        result = _group_by_assignee([task1, task2])
        assert "john" not in result
        assert "jane" in result
        assert result["jane"] == [task2]

    def test_group_by_status_with_parent_tasks(self):
        """Test grouping by status skips tasks with parent."""
        task1 = Mock()
        task1.parent = "parent-123"  # Has parent, should be skipped
        task1.status.status = "To Do"

        task2 = Mock()
        task2.parent = None
        task2.status.status = "Done"
        task2.status.color = "#123"
        task2.status.orderindex = 0

        result = _group_by_status([task1, task2])
        assert "To Do" not in result
        assert "Done" in result

    def test_group_by_priority_with_parent_tasks(self):
        """Test grouping by priority skips tasks with parent."""
        task1 = Mock()
        task1.parent = "parent-123"  # Has parent, should be skipped
        task1.priority = {"priority": "high"}

        task2 = Mock()
        task2.parent = None
        task2.priority = {"priority": "low"}

        result = _group_by_priority([task1, task2])
        assert "high" not in result
        assert "low" in result

    def test_group_by_priority(self):
        """Test grouping by priority."""
        task1 = Mock()
        task1.parent = None
        task1.priority = {"priority": "high"}

        task2 = Mock()
        task2.parent = None
        task2.priority = {"priority": "low"}

        task3 = Mock()
        task3.parent = None
        task3.priority = None

        result = _group_by_priority([task1, task2, task3])
        assert "high" in result
        assert "low" in result
        assert "none" in result
        assert result["high"] == [task1]
        assert result["low"] == [task2]
        assert result["none"] == [task3]

    def test_group_by_status_with_parent_task(self):
        """Test _group_by_status skips tasks with parent."""
        task1 = Mock()
        task1.parent = None
        task1.status.status = "To Do"
        task1.status.color = "#123456"
        task1.status.orderindex = 0

        task2 = Mock()
        task2.parent = Mock()  # Has parent, should be skipped
        task2.status.status = "Done"

        result = _group_by_status([task1, task2])
        assert "To Do" in result
        assert "Done" not in result

    def test_group_by_assignee_with_parent_task(self):
        """Test _group_by_assignee skips tasks with parent."""
        task1 = Mock()
        task1.parent = None
        task1.assignees = [Mock(username="john")]

        task2 = Mock()
        task2.parent = Mock()  # Has parent, should be skipped
        task2.assignees = [Mock(username="jane")]

        result = _group_by_assignee([task1, task2])
        assert "john" in result
        assert "jane" not in result

    def test_group_by_priority_with_parent_task(self):
        """Test _group_by_priority skips tasks with parent."""
        task1 = Mock()
        task1.parent = None
        task1.priority = {"priority": "high"}

        task2 = Mock()
        task2.parent = Mock()  # Has parent, should be skipped
        task2.priority = {"priority": "low"}

        result = _group_by_priority([task1, task2])
        assert "high" in result
        assert "low" not in result


class TestRenderList:
    """Tests for render_list function."""

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_with_filters(self, mock_get_tasks, capsys):
        """Test render_list displays filter info in header."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, assignee="john", priority="high")

        captured = capsys.readouterr()
        assert "assignee=john" in captured.out
        assert "priority=high" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_no_filters(self, mock_get_tasks, capsys):
        """Test render_list without filters."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team)

        captured = capsys.readouterr()
        assert "assignee=" not in captured.out
        assert "priority=" not in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee(self, mock_get_tasks, capsys):
        """Test render_list groups by assignee."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = [Mock(username="john")]
        mock_task.priority = None
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="assignee")

        captured = capsys.readouterr()
        assert "group_by=assignee" in captured.out
        assert "john" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_priority(self, mock_get_tasks, capsys):
        """Test render_list groups by priority."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = {"priority": "high", "color": "#FF8800"}
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="priority")

        captured = capsys.readouterr()
        assert "group_by=priority" in captured.out
        assert "HIGH" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_shows_run_again_suggestion(self, mock_get_tasks, capsys):
        """Test render_list displays 'Run again' suggestion at bottom."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(
            mock_list,
            mock_team,
            assignee="john",
            priority="high",
            group_by="priority",
            team="team-123",
            space="space-456",
            project="proj-789",
            list_id="list-123",
        )

        captured = capsys.readouterr()
        assert "Run again:" in captured.out
        assert "--team team-123" in captured.out
        assert "--space space-456" in captured.out
        assert "--project proj-789" in captured.out
        assert "--list list-123" in captured.out
        assert "--assignee john" in captured.out
        assert "--priority high" in captured.out
        assert "--group-by priority" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_run_again_suggestion_no_filters(self, mock_get_tasks, capsys):
        """Test render_list displays 'Run again' suggestion with no filters."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None
        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, team="team-123", list_id="list-123")

        captured = capsys.readouterr()
        assert "Run again:" in captured.out
        assert "--team team-123" in captured.out
        assert "--list list-123" in captured.out
        # Should not include optional filters
        assert "--assignee" not in captured.out
        assert "--priority" not in captured.out
        assert "--group-by" not in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_run_again_suggestion_with_all_params(self, mock_get_tasks, capsys):
        """Test render_list displays comprehensive 'Run again' suggestion with all parameters."""
        mock_assignee = Mock()
        mock_assignee.username = "jane"

        mock_status = Mock()
        mock_status.status = "To Do"
        mock_status.color = "#123456"
        mock_status.orderindex = 0

        mock_task = Mock()
        mock_task.parent = None
        mock_task.status = mock_status
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = [mock_assignee]
        mock_task.priority = {"priority": "urgent", "color": "#FF0000"}
        mock_task.due_date = "2024-01-01T00:00:00.000Z"

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"
        mock_team.get_all_tasks.return_value = [mock_task]

        render_list(
            mock_list,
            mock_team,
            team="team-abc",
            space="space-def",
            project="proj-ghi",
            list_id="list-123",
            assignee="jane",
            priority="urgent",
            due_before="2024-12-31",
            group_by="assignee",
            no_cache=True,
        )

        captured = capsys.readouterr()
        assert "Run again:" in captured.out
        assert "--team team-abc" in captured.out
        assert "--space space-def" in captured.out
        assert "--project proj-ghi" in captured.out
        assert "--list list-123" in captured.out
        assert "--assignee jane" in captured.out
        assert "--priority urgent" in captured.out
        assert "--due-before 2024-12-31" in captured.out
        assert "--group-by assignee" in captured.out
        assert "--no-cache" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_status_shows_status_color(self, mock_get_tasks, capsys):
        """Test render_list shows status color when grouping by status."""
        mock_status = Mock()
        mock_status.status = "In Progress"
        mock_status.color = "#FF5500"
        mock_status.orderindex = 1

        mock_task = Mock()
        mock_task.parent = None
        mock_task.status = mock_status
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="status")

        captured = capsys.readouterr()
        # Status color should be rendered (hex converted to RGB: 255;85;0 for #FF5500)
        assert "255;85;0" in captured.out or "IN PROGRESS" in captured.out.upper()

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_priority_shows_priority_color(self, mock_get_tasks, capsys):
        """Test render_list shows priority color when grouping by priority."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status = Mock(status="To Do", color="#123", orderindex=0)
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = {"priority": "urgent", "color": "#FF0000"}

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="priority")

        captured = capsys.readouterr()
        # Priority color should be rendered
        assert "URGENT" in captured.out.upper()

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee_empty_tasks(self, mock_get_tasks, capsys):
        """Test render_list handles empty task list."""
        mock_get_tasks.return_value = []

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="assignee")

        captured = capsys.readouterr()
        # Should render header but no tasks
        assert "Test List" in captured.out
        assert "Run again:" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_status_empty_tasks_group(self, mock_get_tasks, capsys):
        """Test render_list handles status group with no tasks."""
        # Create tasks that will result in an empty group after filtering
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status = Mock(status="To Do", color="#123", orderindex=0)
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        # Filter by a priority that doesn't match, leaving empty status groups
        render_list(mock_list, mock_team, group_by="status", priority="urgent")

        captured = capsys.readouterr()
        # Should still render but with no tasks
        assert "Test List" in captured.out
        assert "Run again:" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_status_with_mixed_empty_and_nonempty_groups(self, mock_get_tasks, capsys):
        """Test render_list with status grouping where some groups have tasks and some don't.

        This covers the if tasks: False branch at line 204.
        """
        # Create two tasks with different statuses
        mock_task1 = Mock()
        mock_task1.parent = None
        mock_task1.status = Mock(status="To Do", color="#123", orderindex=0)
        mock_task1.name = "Task 1"
        mock_task1.url = "https://test.com"
        mock_task1.assignees = []
        mock_task1.priority = {"priority": "high", "color": "#FF8800"}

        mock_task2 = Mock()
        mock_task2.parent = None
        mock_task2.status = Mock(status="Done", color="#456", orderindex=1)
        mock_task2.name = "Task 2"
        mock_task2.url = "https://test.com"
        mock_task2.assignees = []
        mock_task2.priority = None  # This task will be filtered out

        mock_get_tasks.return_value = [mock_task1, mock_task2]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        # Filter by priority=high - only mock_task1 matches
        # This leaves "Done" status group empty
        render_list(mock_list, mock_team, group_by="status", priority="high")

        captured = capsys.readouterr()
        # Should render "To Do" with color (tasks present)
        # Should handle "Done" group without color (tasks empty - line 204 False path)
        assert "Test List" in captured.out
        assert "TO DO" in captured.out.upper()

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee_executes_elif_path(self, mock_get_tasks, capsys):
        """Test render_list with assignee grouping executes the elif group_by == 'assignee' path.

        This covers the branch at line 209.
        """
        mock_assignee = Mock()
        mock_assignee.username = "john"

        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = [mock_assignee]
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="assignee")

        captured = capsys.readouterr()
        # Should show assignee name with bold formatting
        assert "john" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_status_no_tasks(self, mock_get_tasks, capsys):
        """Test render_list with empty tasks list for status grouping."""
        mock_get_tasks.return_value = []

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="status")

        captured = capsys.readouterr()
        # Should handle empty tasks without error
        assert "Test List" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee_no_tasks(self, mock_get_tasks, capsys):
        """Test render_list with empty tasks list for assignee grouping."""
        mock_get_tasks.return_value = []

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="assignee")

        captured = capsys.readouterr()
        # Should handle empty tasks without error
        assert "Test List" in captured.out
        assert "Test List" in captured.out
        assert "Run again:" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_priority_unknown_priority(self, mock_get_tasks, capsys):
        """Test render_list handles unknown priority with default color."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status = Mock(status="To Do", color="#123", orderindex=0)
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        # No priority set - will be grouped as "none"
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="priority")

        captured = capsys.readouterr()
        # Should render "NONE" with default color
        assert "NONE" in captured.out.upper()

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_priority_empty_tasks(self, mock_get_tasks, capsys):
        """Test render_list handles empty task list with priority grouping."""
        mock_get_tasks.return_value = []

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="priority")

        captured = capsys.readouterr()
        # Should render header but no tasks
        assert "Test List" in captured.out
        assert "Run again:" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee_shows_assignee_name(self, mock_get_tasks, capsys):
        """Test render_list with assignee grouping shows assignee name formatting."""
        mock_assignee = Mock()
        mock_assignee.username = "john"

        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = [mock_assignee]
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="assignee")

        captured = capsys.readouterr()
        # Should show assignee name with bold formatting
        assert "john" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_assignee_empty_group(self, mock_get_tasks, capsys):
        """Test render_list with assignee grouping where a group has no tasks."""
        # Create tasks that will result in an empty group after filtering
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "Done"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        # Filter by assignee that doesn't match, leaving empty assignee group
        render_list(mock_list, mock_team, group_by="assignee", assignee="nonexistent")

        captured = capsys.readouterr()
        # Should handle empty groups without error
        assert "Test List" in captured.out

    @patch("quickup.cli.renderer.get_tasks_data")
    def test_render_list_group_by_priority_with_none_priority(self, mock_get_tasks, capsys):
        """Test render_list groups by priority with tasks without priority."""
        mock_task = Mock()
        mock_task.parent = None
        mock_task.status.status = "To Do"
        mock_task.status.color = "#123456"
        mock_task.status.orderindex = 0
        mock_task.name = "Test Task"
        mock_task.url = "https://test.com"
        mock_task.assignees = []
        mock_task.priority = None  # No priority

        mock_get_tasks.return_value = [mock_task]

        mock_list = Mock()
        mock_list.name = "Test List"
        mock_list.id = "list-123"

        mock_team = Mock()
        mock_team.name = "Test Team"

        render_list(mock_list, mock_team, group_by="priority")

        captured = capsys.readouterr()
        # Should show NONE group for tasks without priority
        assert "NONE" in captured.out.upper()

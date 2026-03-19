"""Tests for KeyUp! renderer module."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from keyup.cli.renderer import _filter_tasks, render_list


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

    def test_priority_filter_no_priority(self):
        """Test priority filter excludes tasks without priority."""
        task1 = Mock()
        task1.priority = {"priority": "high"}
        task2 = Mock()
        task2.priority = None

        result = _filter_tasks([task1, task2], priority="high")
        assert result == [task1]

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


class TestRenderList:
    """Tests for render_list function."""

    @patch("keyup.cli.renderer.get_tasks_data")
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

    @patch("keyup.cli.renderer.get_tasks_data")
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

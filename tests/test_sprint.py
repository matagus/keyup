"""Tests for KeyUp! sprint command."""

import pytest
from unittest.mock import Mock

from keyup.cli.api_client import get_current_sprint_list


class TestGetCurrentSprintList:
    """Tests for get_current_sprint_list function."""

    def test_finds_sprint_list(self):
        """Test finding a sprint list."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        sprint_list = Mock()
        sprint_list.name = "Sprint 5"
        sprint_list.id = "list-005"
        sprint_list.space_id = "space-123"

        other_list = Mock()
        other_list.name = "Backlog"
        other_list.id = "list-001"
        other_list.space_id = "space-123"

        mock_team.lists = [sprint_list, other_list]

        result = get_current_sprint_list(mock_team, mock_space)
        assert result == sprint_list

    def test_finds_iteration_list(self):
        """Test finding an iteration list."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        iteration_list = Mock()
        iteration_list.name = "Iteration 3"
        iteration_list.id = "list-003"
        iteration_list.space_id = "space-123"

        mock_team.lists = [iteration_list]

        result = get_current_sprint_list(mock_team, mock_space)
        assert result == iteration_list

    def test_returns_most_recent_sprint(self):
        """Test returning the most recent sprint by ID."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        sprint_old = Mock()
        sprint_old.name = "Sprint 1"
        sprint_old.id = "list-001"
        sprint_old.space_id = "space-123"

        sprint_new = Mock()
        sprint_new.name = "Sprint 2"
        sprint_new.id = "list-002"
        sprint_new.space_id = "space-123"

        mock_team.lists = [sprint_old, sprint_new]

        result = get_current_sprint_list(mock_team, mock_space)
        assert result == sprint_new

    def test_filters_by_space(self):
        """Test filtering lists by space."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        sprint_correct = Mock()
        sprint_correct.name = "Sprint"
        sprint_correct.id = "list-001"
        sprint_correct.space_id = "space-123"

        sprint_other = Mock()
        sprint_other.name = "Sprint Other"
        sprint_other.id = "list-002"
        sprint_other.space_id = "space-456"

        mock_team.lists = [sprint_correct, sprint_other]

        result = get_current_sprint_list(mock_team, mock_space)
        assert result == sprint_correct

    def test_no_sprint_lists_raises_error(self):
        """Test raising error when no sprint lists found."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        backlog = Mock()
        backlog.name = "Backlog"
        backlog.id = "list-001"
        backlog.space_id = "space-123"

        mock_team.lists = [backlog]

        with pytest.raises(Exception):  # ListNotFoundError
            get_current_sprint_list(mock_team, mock_space)

    def test_case_insensitive_search(self):
        """Test case-insensitive sprint search."""
        mock_team = Mock()
        mock_space = Mock(id="space-123")

        sprint_list = Mock()
        sprint_list.name = "SPRINT 5"
        sprint_list.id = "list-005"
        sprint_list.space_id = "space-123"

        mock_team.lists = [sprint_list]

        result = get_current_sprint_list(mock_team, mock_space)
        assert result == sprint_list

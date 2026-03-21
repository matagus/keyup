"""Reusable test fixtures for KeyUp! CLI tests."""

from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_team():
    """Create a mock team object."""
    team = Mock()
    team.id = "team-123"
    team.name = "Test Team"
    team.spaces = []
    return team


@pytest.fixture
def mock_space():
    """Create a mock space object."""
    space = Mock()
    space.id = "space-456"
    space.name = "Test Space"
    space.projects = []
    space.lists = []
    return space


@pytest.fixture
def mock_project():
    """Create a mock project object."""
    project = Mock()
    project.id = "project-789"
    project.name = "Test Project"
    return project


@pytest.fixture
def mock_list():
    """Create a mock list object."""
    list_obj = Mock()
    list_obj.id = "list-000"
    list_obj.name = "Test List"
    return list_obj


@pytest.fixture
def mock_task():
    """Create a mock task object."""
    task = Mock()
    task.id = "task-111"
    task.name = "Test Task"
    task.url = "https://app.clickup.com/t/task-111"
    task.parent = None
    task.assignees = []
    task.priority = None
    task.status = Mock()
    task.status.status = "To Do"
    task.status.color = "#CCCCCC"
    task.status.orderindex = 0
    return task


@pytest.fixture
def mock_clickup():
    """Create a mock ClickUp client."""
    clickup = Mock()
    clickup.teams = []
    return clickup

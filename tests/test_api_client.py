"""Tests for KeyUp! API client module."""

import pytest
from unittest.mock import Mock, patch

from keyup.cli.api_client import (
    get_team,
    get_space_for,
    get_project_for,
    get_list_for,
    get_current_sprint_list,
)
from keyup.cli.exceptions import (
    TeamNotFoundError,
    TeamAmbiguousError,
    SpaceNotFoundError,
    ProjectNotFoundError,
    ListNotFoundError,
)


class TestGetTeam:
    """Tests for get_team function."""

    def setup_method(self):
        self.patch_get_teams = patch("keyup.cli.api_client.get_teams_data", side_effect=lambda c: c.teams)
        self.patch_get_teams.start()

    def teardown_method(self):
        self.patch_get_teams.stop()

    @patch("sys.argv", ["keyup", "--team", "team-123"])
    def test_with_team_flag(self):
        """Test with --team flag provided."""
        mock_clickup = Mock()
        mock_team = Mock(id="team-123")
        mock_clickup.teams = [mock_team]

        result = get_team(mock_clickup, ["--team", "team-123"])

        assert result is mock_team

    @patch("sys.argv", ["keyup"])
    def test_no_teams_raises_error(self):
        """Test with no teams available raises TeamNotFoundError."""
        mock_clickup = Mock()
        mock_clickup.teams = []

        with pytest.raises(TeamNotFoundError):
            get_team(mock_clickup, [])

    @patch("sys.argv", ["keyup"])
    def test_multiple_teams_interactive(self):
        """Test with multiple teams and interactive=True prompts user."""
        mock_clickup = Mock()
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Team A"
        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Team B"
        mock_clickup.teams = [mock_team1, mock_team2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"team": "Team A [team-1]"}

            result = get_team(mock_clickup, [], interactive=True)

            assert result is mock_team1

    @patch("sys.argv", ["keyup"])
    def test_multiple_teams_interactive_no_answer(self):
        """Test with multiple teams and interactive=True but prompt returns None."""
        mock_clickup = Mock()
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Team A"
        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Team B"
        mock_clickup.teams = [mock_team1, mock_team2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = None

            # When no answer, falls through to raise TeamAmbiguousError
            with pytest.raises(TeamAmbiguousError):
                get_team(mock_clickup, [], interactive=True)

    @patch("sys.argv", ["keyup"])
    def test_multiple_teams_interactive_invalid_answer(self):
        """Test with multiple teams and interactive=True but answer doesn't match any team."""
        mock_clickup = Mock()
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Team A"
        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Team B"
        mock_clickup.teams = [mock_team1, mock_team2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"team": "Nonexistent Team [team-999]"}

            # When answer doesn't match, falls through to raise TeamAmbiguousError
            with pytest.raises(TeamAmbiguousError):
                get_team(mock_clickup, [], interactive=True)

    @patch("sys.argv", ["keyup"])
    def test_multiple_teams_interactive_no_match(self):
        """Test with multiple teams and interactive=True but answer doesn't match any team."""
        mock_clickup = Mock()
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Team A"
        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Team B"
        mock_clickup.teams = [mock_team1, mock_team2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"team": "Nonexistent Team [team-999]"}

            # When answer doesn't match, falls through to raise TeamAmbiguousError
            with pytest.raises(TeamAmbiguousError):
                get_team(mock_clickup, [], interactive=True)

    @patch("sys.argv", ["keyup"])
    def test_multiple_teams_non_interactive_raises(self):
        """Test with multiple teams and interactive=False raises TeamAmbiguousError."""
        mock_clickup = Mock()
        mock_team1 = Mock()
        mock_team1.id = "team-1"
        mock_team1.name = "Team A"
        mock_team2 = Mock()
        mock_team2.id = "team-2"
        mock_team2.name = "Team B"
        mock_clickup.teams = [mock_team1, mock_team2]

        with pytest.raises(TeamAmbiguousError) as exc_info:
            get_team(mock_clickup, [], interactive=False)

        assert "Team A" in str(exc_info.value)
        assert "Team B" in str(exc_info.value)

    @patch("sys.argv", ["keyup"])
    def test_single_team_returns_first(self):
        """Test with single team returns first team."""
        mock_clickup = Mock()
        mock_team = Mock(id="team-1", name="Solo Team")
        mock_clickup.teams = [mock_team]

        result = get_team(mock_clickup, [])

        assert result is mock_team

    @patch("sys.argv", ["keyup", "--team", "invalid-id"])
    def test_invalid_team_id_raises_error(self):
        """Test with invalid team ID raises TeamNotFoundError with team_id."""
        mock_clickup = Mock()
        mock_clickup.teams = [Mock(id="team-1")]
        mock_clickup.get_team_by_id.side_effect = Exception("Invalid ID")

        with pytest.raises(TeamNotFoundError) as exc_info:
            get_team(mock_clickup, ["--team", "invalid-id"])

        assert exc_info.value.message == "Team 'invalid-id' not found."


class TestGetSpaceFor:
    """Tests for get_space_for function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_team = Mock()
        self.patch_get_spaces = patch("keyup.cli.api_client.get_spaces_data", side_effect=lambda t: t.spaces)
        self.patch_get_spaces.start()

    def teardown_method(self):
        self.patch_get_spaces.stop()

    @patch("sys.argv", ["keyup", "--space", "space-456"])
    def test_with_space_flag(self):
        """Test with --space flag provided."""
        mock_space = Mock(id="space-456")
        self.mock_team.spaces = [mock_space]

        result = get_space_for(self.mock_team, ["--space", "space-456"])

        assert result is mock_space

    @patch("sys.argv", ["keyup"])
    def test_no_spaces_raises_error(self):
        """Test with no spaces available raises SpaceNotFoundError."""
        self.mock_team.spaces = []

        with pytest.raises(SpaceNotFoundError):
            get_space_for(self.mock_team, [])

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_interactive(self):
        """Test with multiple spaces and interactive=True."""
        mock_space1 = Mock(id="space-1", name="Space A")
        mock_space2 = Mock(id="space-2", name="Space B")
        self.mock_team.spaces = [mock_space1, mock_space2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"space": "Space A [space-1]"}

            result = get_space_for(self.mock_team, [], interactive=True)

            assert result is mock_space1

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_interactive_no_answer(self):
        """Test with multiple spaces and interactive=True but prompt returns None."""
        mock_space1 = Mock(id="space-1", name="Space A")
        mock_space2 = Mock(id="space-2", name="Space B")
        self.mock_team.spaces = [mock_space1, mock_space2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = None

            # When no answer, returns first space
            result = get_space_for(self.mock_team, [], interactive=True)
            assert result is mock_space1

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_interactive_selects_second(self):
        """Test with multiple spaces and interactive=True selects correct space."""
        mock_space1 = Mock()
        mock_space1.id = "space-1"
        mock_space1.name = "Space A"
        mock_space2 = Mock()
        mock_space2.id = "space-2"
        mock_space2.name = "Space B"
        self.mock_team.spaces = [mock_space1, mock_space2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"space": "Space B [space-2]"}

            result = get_space_for(self.mock_team, [], interactive=True)

            assert result is mock_space2

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_interactive_invalid_answer(self):
        """Test with multiple spaces and interactive=True but answer doesn't match."""
        mock_space1 = Mock()
        mock_space1.id = "space-1"
        mock_space1.name = "Space A"
        mock_space2 = Mock()
        mock_space2.id = "space-2"
        mock_space2.name = "Space B"
        self.mock_team.spaces = [mock_space1, mock_space2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"space": "Nonexistent Space [space-999]"}

            # When answer doesn't match, returns first space
            result = get_space_for(self.mock_team, [], interactive=True)
            assert result is mock_space1

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_non_interactive_returns_first(self):
        """Test with multiple spaces returns first when not interactive."""
        mock_space1 = Mock(id="space-1", name="Space A")
        mock_space2 = Mock(id="space-2", name="Space B")
        self.mock_team.spaces = [mock_space1, mock_space2]

        result = get_space_for(self.mock_team, [], interactive=False)

        assert result is mock_space1

    @patch("sys.argv", ["keyup"])
    def test_multiple_spaces_interactive_false_explicit(self):
        """Test with multiple spaces and interactive=False explicitly."""
        mock_space1 = Mock(id="space-1", name="Space A")
        mock_space2 = Mock(id="space-2", name="Space B")
        self.mock_team.spaces = [mock_space1, mock_space2]

        # Explicitly pass interactive=False
        result = get_space_for(self.mock_team, [], interactive=False)

        assert result is mock_space1

    @patch("sys.argv", ["keyup", "--space", "invalid-id"])
    def test_invalid_space_id_raises_error(self):
        """Test with invalid space ID raises SpaceNotFoundError with space_id."""
        self.mock_team.spaces = [Mock(id="space-1")]

        with pytest.raises(SpaceNotFoundError) as exc_info:
            get_space_for(self.mock_team, ["--space", "invalid-id"])

        assert exc_info.value.message == "Space 'invalid-id' not found."


class TestGetProjectFor:
    """Tests for get_project_for function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_space = Mock()
        self.patch_get_projects = patch("keyup.cli.api_client.get_projects_data", side_effect=lambda s: s.projects)
        self.patch_get_projects.start()

    def teardown_method(self):
        self.patch_get_projects.stop()

    @patch("sys.argv", ["keyup", "--project", "project-789"])
    def test_with_project_flag(self):
        """Test with --project flag provided."""
        mock_project = Mock(id="project-789")
        self.mock_space.projects = [mock_project]

        result = get_project_for(self.mock_space, ["--project", "project-789"])

        assert result is mock_project

    @patch("sys.argv", ["keyup"])
    def test_no_projects_raises_error(self):
        """Test with no projects available raises ProjectNotFoundError."""
        self.mock_space.projects = []

        with pytest.raises(ProjectNotFoundError):
            get_project_for(self.mock_space, [])

    @patch("sys.argv", ["keyup"])
    def test_multiple_projects_interactive(self):
        """Test with multiple projects and interactive=True."""
        mock_proj1 = Mock(id="proj-1", name="Project A")
        mock_proj2 = Mock(id="proj-2", name="Project B")
        self.mock_space.projects = [mock_proj1, mock_proj2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"project": "Project A [proj-1]"}

            result = get_project_for(self.mock_space, [], interactive=True)

            assert result is mock_proj1

    @patch("sys.argv", ["keyup"])
    def test_multiple_projects_interactive_no_answer(self):
        """Test with multiple projects and interactive=True but prompt returns None."""
        mock_proj1 = Mock(id="proj-1", name="Project A")
        mock_proj2 = Mock(id="proj-2", name="Project B")
        self.mock_space.projects = [mock_proj1, mock_proj2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = None

            # When no answer, returns first project
            result = get_project_for(self.mock_space, [], interactive=True)
            assert result is mock_proj1

    @patch("sys.argv", ["keyup"])
    def test_multiple_projects_interactive_selects_second(self):
        """Test with multiple projects and interactive=True selects correct project."""
        mock_proj1 = Mock()
        mock_proj1.id = "proj-1"
        mock_proj1.name = "Project A"
        mock_proj2 = Mock()
        mock_proj2.id = "proj-2"
        mock_proj2.name = "Project B"
        self.mock_space.projects = [mock_proj1, mock_proj2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"project": "Project B [proj-2]"}

            result = get_project_for(self.mock_space, [], interactive=True)

            assert result is mock_proj2

    @patch("sys.argv", ["keyup"])
    def test_multiple_projects_interactive_invalid_answer(self):
        """Test with multiple projects and interactive=True but answer doesn't match."""
        mock_proj1 = Mock()
        mock_proj1.id = "proj-1"
        mock_proj1.name = "Project A"
        mock_proj2 = Mock()
        mock_proj2.id = "proj-2"
        mock_proj2.name = "Project B"
        self.mock_space.projects = [mock_proj1, mock_proj2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"project": "Nonexistent Project [proj-999]"}

            # When answer doesn't match, returns first project
            result = get_project_for(self.mock_space, [], interactive=True)
            assert result is mock_proj1

    @patch("sys.argv", ["keyup"])
    def test_multiple_projects_non_interactive_returns_first(self):
        """Test with multiple projects returns first when not interactive."""
        mock_proj1 = Mock(id="proj-1", name="Project A")
        mock_proj2 = Mock(id="proj-2", name="Project B")
        self.mock_space.projects = [mock_proj1, mock_proj2]

        result = get_project_for(self.mock_space, [], interactive=False)

        assert result is mock_proj1

    @patch("sys.argv", ["keyup", "--project", "invalid-id"])
    def test_invalid_project_id_raises_error(self):
        """Test with invalid project ID raises ProjectNotFoundError with project_id."""
        self.mock_space.projects = [Mock(id="proj-1")]

        with pytest.raises(ProjectNotFoundError) as exc_info:
            get_project_for(self.mock_space, ["--project", "invalid-id"])

        assert exc_info.value.message == "Project 'invalid-id' not found."


class TestGetListFor:
    """Tests for get_list_for function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_space = Mock()
        self.patch_get_lists = patch("keyup.cli.api_client.get_lists_data", side_effect=lambda p: p.lists)
        self.patch_get_lists.start()

    def teardown_method(self):
        self.patch_get_lists.stop()

    @patch("sys.argv", ["keyup", "--list", "list-000"])
    def test_with_list_flag(self):
        """Test with --list flag provided."""
        mock_list = Mock(id="list-000")
        self.mock_space.lists = [mock_list]

        result = get_list_for(self.mock_space, ["--list", "list-000"])

        assert result is mock_list

    @patch("sys.argv", ["keyup"])
    def test_no_lists_raises_error(self):
        """Test with no lists available raises ListNotFoundError."""
        self.mock_space.lists = []

        with pytest.raises(ListNotFoundError):
            get_list_for(self.mock_space, [])

    @patch("sys.argv", ["keyup"])
    def test_multiple_lists_interactive(self):
        """Test with multiple lists and interactive=True."""
        mock_list1 = Mock(id="list-1", name="List A")
        mock_list2 = Mock(id="list-2", name="List B")
        self.mock_space.lists = [mock_list1, mock_list2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"list": "List A [list-1]"}

            result = get_list_for(self.mock_space, [], interactive=True)

            assert result is mock_list1

    @patch("sys.argv", ["keyup"])
    def test_multiple_lists_interactive_no_answer(self):
        """Test with multiple lists and interactive=True but prompt returns None."""
        mock_list1 = Mock(id="list-1", name="List A")
        mock_list2 = Mock(id="list-2", name="List B")
        self.mock_space.lists = [mock_list1, mock_list2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = None

            # When no answer, returns first list
            result = get_list_for(self.mock_space, [], interactive=True)
            assert result is mock_list1

    @patch("sys.argv", ["keyup"])
    def test_multiple_lists_interactive_selects_second(self):
        """Test with multiple lists and interactive=True selects correct list."""
        mock_list1 = Mock()
        mock_list1.id = "list-1"
        mock_list1.name = "List A"
        mock_list2 = Mock()
        mock_list2.id = "list-2"
        mock_list2.name = "List B"
        self.mock_space.lists = [mock_list1, mock_list2]

        with patch("inquirer.prompt") as mock_prompt:
            mock_prompt.return_value = {"list": "List B [list-2]"}

            result = get_list_for(self.mock_space, [], interactive=True)

            assert result is mock_list2

    @patch("sys.argv", ["keyup"])
    def test_multiple_lists_non_interactive_returns_first(self):
        """Test with multiple lists returns first when not interactive."""
        mock_list1 = Mock(id="list-1", name="List A")
        mock_list2 = Mock(id="list-2", name="List B")
        self.mock_space.lists = [mock_list1, mock_list2]

        result = get_list_for(self.mock_space, [], interactive=False)

        assert result is mock_list1

    @patch("sys.argv", ["keyup", "--list", "invalid-id"])
    def test_invalid_list_id_raises_error(self):
        """Test with invalid list ID raises ListNotFoundError with list_id."""
        self.mock_space.lists = [Mock(id="list-1")]

        with pytest.raises(ListNotFoundError) as exc_info:
            get_list_for(self.mock_space, ["--list", "invalid-id"])

        assert exc_info.value.message == "List 'invalid-id' not found."


class TestGetCurrentSprintList:
    """Tests for get_current_sprint_list function."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_team = Mock()
        self.mock_space = Mock()
        self.patch_get_spaces = patch("keyup.cli.api_client.get_spaces_data", side_effect=lambda t: t.spaces)
        self.patch_get_projects = patch("keyup.cli.api_client.get_projects_data", side_effect=lambda s: s.projects)
        self.patch_get_lists = patch("keyup.cli.api_client.get_lists_data", side_effect=lambda p: p.lists)
        self.patch_get_spaces.start()
        self.patch_get_projects.start()
        self.patch_get_lists.start()

    def teardown_method(self):
        self.patch_get_spaces.stop()
        self.patch_get_projects.stop()
        self.patch_get_lists.stop()

    def test_finds_sprint_lists(self):
        """Test finds sprint lists (case-insensitive 'sprint' match)."""
        mock_list = Mock()
        mock_list.id = "123"
        mock_list.name = "Sprint 1"
        mock_proj = Mock()
        mock_proj.lists = [mock_list]
        self.mock_space.projects = [mock_proj]
        self.mock_team.spaces = [self.mock_space]

        result = get_current_sprint_list(self.mock_team, self.mock_space)

        assert result is mock_list

    def test_finds_iteration_lists(self):
        """Test finds iteration lists (case-insensitive 'iteration' match)."""
        mock_list = Mock()
        mock_list.id = "456"
        mock_list.name = "Iteration 2"
        mock_proj = Mock()
        mock_proj.lists = [mock_list]
        self.mock_space.projects = [mock_proj]
        self.mock_team.spaces = [self.mock_space]

        result = get_current_sprint_list(self.mock_team, self.mock_space)

        assert result is mock_list

    def test_returns_most_recent_sprint(self):
        """Test returns most recent sprint (sorted by ID descending)."""
        mock_list1 = Mock()
        mock_list1.id = "100"
        mock_list1.name = "Sprint 1"
        mock_list2 = Mock()
        mock_list2.id = "200"
        mock_list2.name = "Sprint 2"
        mock_proj = Mock()
        mock_proj.lists = [mock_list1, mock_list2]
        self.mock_space.projects = [mock_proj]
        self.mock_team.spaces = [self.mock_space]

        result = get_current_sprint_list(self.mock_team, self.mock_space)

        assert result is mock_list2  # Higher ID (more recent)

    def test_filters_by_space_parameter(self):
        """Test filters by space parameter."""
        mock_list1 = Mock()
        mock_list1.id = "100"
        mock_list1.name = "Sprint A"
        mock_proj1 = Mock()
        mock_proj1.lists = [mock_list1]

        mock_list2 = Mock()
        mock_list2.id = "200"
        mock_list2.name = "Sprint B"
        mock_proj2 = Mock()
        mock_proj2.lists = [mock_list2]

        mock_space1 = Mock(projects=[mock_proj1])
        mock_space2 = Mock(projects=[mock_proj2])
        self.mock_team.spaces = [mock_space1, mock_space2]

        # When space is specified, only that space's projects are searched
        result = get_current_sprint_list(self.mock_team, mock_space2)

        assert result is mock_list2

    def test_raises_error_when_no_sprint_lists_found(self):
        """Test raises error when no sprint lists found."""
        mock_list = Mock()
        mock_list.id = "100"
        mock_list.name = "Backlog"  # No "sprint" or "iteration" in name
        mock_proj = Mock()
        mock_proj.lists = [mock_list]
        self.mock_space.projects = [mock_proj]
        self.mock_team.spaces = [self.mock_space]

        with pytest.raises(ListNotFoundError) as exc_info:
            get_current_sprint_list(self.mock_team, self.mock_space)

        assert "No lists found with 'sprint' or 'iteration' in the name" in str(exc_info.value)

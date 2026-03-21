"""Tests for KeyUp! cache module."""

from pathlib import Path
from unittest.mock import Mock, patch

from keyup.cli.cache import (
    get_cache,
    get_teams_data,
    get_spaces_data,
    get_projects_data,
    get_lists_data,
    get_tasks_data,
    find_task_in_cache,
    get_task_data,
    invalidate_tasks_cache,
    clear_cache,
    TEAMS_TTL,
    SPACES_TTL,
    PROJECTS_TTL,
    LISTS_TTL,
    TASKS_TTL,
)


class TestGetCache:
    """Tests for get_cache function."""

    def test_get_cache_creates_directory(self, tmp_path):
        """Test that get_cache creates the cache directory."""
        import shutil

        cache_dir = Path.home() / ".keyup" / "cache"
        backup_path = tmp_path / "keyup_cache_backup"

        # Backup existing cache dir if present
        if cache_dir.exists():
            shutil.move(str(cache_dir), str(backup_path))

        try:
            get_cache()
            assert cache_dir.exists()
            assert cache_dir.is_dir()
        finally:
            # Restore backup
            if backup_path.exists():
                if cache_dir.exists():
                    shutil.rmtree(str(cache_dir))
                shutil.move(str(backup_path), str(cache_dir))

    @patch("keyup.cli.cache.SQLiteCache")
    @patch("keyup.cli.cache.Path")
    def test_get_cache_returns_cache_instance(self, mock_path_class, mock_sqlite_cache):
        """Test that get_cache returns a SQLiteCache instance."""
        mock_path_class.return_value = Mock()
        cache = get_cache()
        assert cache is mock_sqlite_cache.return_value


class TestGetTeamsData:
    """Tests for get_teams_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_team"])
        mock_get_cache.return_value = mock_cache

        result = get_teams_data(Mock())

        assert result == ["cached_team"]
        mock_cache.get.assert_called_once_with("teams")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_clickup = Mock()
        mock_clickup.teams = ["api_team"]

        result = get_teams_data(mock_clickup)

        assert result == ["api_team"]
        mock_cache.set.assert_called_once_with("teams", ["api_team"], expire=TEAMS_TTL)


class TestGetSpacesData:
    """Tests for get_spaces_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_space"])
        mock_get_cache.return_value = mock_cache

        result = get_spaces_data(Mock(id="team-123"))

        assert result == ["cached_space"]
        mock_cache.get.assert_called_once_with("spaces:team-123")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_team = Mock(id="team-123")
        mock_team.spaces = ["api_space"]

        result = get_spaces_data(mock_team)

        assert result == ["api_space"]
        mock_cache.set.assert_called_once_with("spaces:team-123", ["api_space"], expire=SPACES_TTL)


class TestGetProjectsData:
    """Tests for get_projects_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_project"])
        mock_get_cache.return_value = mock_cache

        result = get_projects_data(Mock(id="space-123"))

        assert result == ["cached_project"]
        mock_cache.get.assert_called_once_with("projects:space-123")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_space = Mock(id="space-123")
        mock_space.projects = ["api_project"]

        result = get_projects_data(mock_space)

        assert result == ["api_project"]
        mock_cache.set.assert_called_once_with("projects:space-123", ["api_project"], expire=PROJECTS_TTL)


class TestGetListsData:
    """Tests for get_lists_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_list"])
        mock_get_cache.return_value = mock_cache

        result = get_lists_data(Mock(id="project-123"))

        assert result == ["cached_list"]
        mock_cache.get.assert_called_once_with("lists:project-123")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_project = Mock(id="project-123")
        mock_project.lists = ["api_list"]

        result = get_lists_data(mock_project)

        assert result == ["api_list"]
        mock_cache.set.assert_called_once_with("lists:project-123", ["api_list"], expire=LISTS_TTL)


class TestGetTasksData:
    """Tests for get_tasks_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_task"])
        mock_get_cache.return_value = mock_cache

        mock_team = Mock()
        result = get_tasks_data(mock_team, "list-000")

        assert result == ["cached_task"]
        mock_cache.get.assert_called_once_with("tasks:list-000")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_team = Mock()
        mock_team.get_all_tasks.return_value = ["api_task"]

        result = get_tasks_data(mock_team, "list-000")

        assert result == ["api_task"]
        mock_team.get_all_tasks.assert_called_once_with(subtasks=False, list_ids=["list-000"])
        mock_cache.set.assert_called_once_with("tasks:list-000", ["api_task"], expire=TASKS_TTL)


class TestFindTaskInCache:
    """Tests for find_task_in_cache function."""

    @patch("keyup.cli.cache.get_cache")
    def test_found_via_task_key(self, mock_get_cache):
        """Test task found via direct task cache key."""
        mock_task = Mock(id="task-abc")
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=mock_task)
        mock_get_cache.return_value = mock_cache

        result = find_task_in_cache("task-abc")

        assert result is mock_task
        mock_cache.get.assert_called_once_with("task:task-abc")

    @patch("keyup.cli.cache.get_cache")
    def test_found_in_list_cache(self, mock_get_cache):
        """Test task found by searching cached task lists."""
        mock_task = Mock(id="task-abc")
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_cache.get_all_by_prefix = Mock(return_value=[[Mock(id="task-xyz"), mock_task]])
        mock_get_cache.return_value = mock_cache

        result = find_task_in_cache("task-abc")

        assert result is mock_task
        mock_cache.get_all_by_prefix.assert_called_once_with("tasks:")

    @patch("keyup.cli.cache.get_cache")
    def test_not_found_in_cache(self, mock_get_cache):
        """Test returns None when task not in any cached list."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_cache.get_all_by_prefix = Mock(return_value=[[Mock(id="task-xyz")]])
        mock_get_cache.return_value = mock_cache

        result = find_task_in_cache("task-abc")

        assert result is None

    @patch("keyup.cli.cache.get_cache")
    def test_empty_cache(self, mock_get_cache):
        """Test returns None when cache is empty."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_cache.get_all_by_prefix = Mock(return_value=[])
        mock_get_cache.return_value = mock_cache

        result = find_task_in_cache("task-abc")

        assert result is None


class TestGetTaskData:
    """Tests for get_task_data function."""

    @patch("keyup.cli.cache.find_task_in_cache")
    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache, mock_find):
        """Test returns cached task without calling API."""
        mock_task = Mock(id="task-abc")
        mock_find.return_value = mock_task
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        result = get_task_data(Mock(), "team-123", "task-abc")

        assert result is mock_task
        mock_cache.set.assert_called_once_with("task:task-abc", mock_task, expire=TASKS_TTL)

    @patch("keyup.cli.cache.find_task_in_cache")
    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss_fetches_from_api(self, mock_get_cache, mock_find):
        """Test falls back to API and caches the result."""
        mock_task = Mock(id="task-abc")
        mock_find.return_value = None
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        mock_clickup = Mock()
        mock_clickup._get_all_tasks.return_value = [Mock(id="task-xyz"), mock_task]

        result = get_task_data(mock_clickup, "team-123", "task-abc")

        assert result is mock_task
        mock_clickup._get_all_tasks.assert_called_once_with("team-123")
        mock_cache.set.assert_called_once_with("task:task-abc", mock_task, expire=TASKS_TTL)

    @patch("keyup.cli.cache.find_task_in_cache")
    @patch("keyup.cli.cache.get_cache")
    def test_not_found_returns_none(self, mock_get_cache, mock_find):
        """Test returns None when task not found anywhere."""
        mock_find.return_value = None
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        mock_clickup = Mock()
        mock_clickup._get_all_tasks.return_value = [Mock(id="task-xyz")]

        result = get_task_data(mock_clickup, "team-123", "task-abc")

        assert result is None
        mock_cache.set.assert_not_called()


class TestInvalidateTasksCache:
    """Tests for invalidate_tasks_cache function."""

    @patch("keyup.cli.cache.get_cache")
    def test_invalidate(self, mock_get_cache):
        """Test cache invalidation."""
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        invalidate_tasks_cache("list-000")

        mock_cache.delete.assert_called_once_with("tasks:list-000")


class TestClearCache:
    """Tests for clear_cache function."""

    @patch("keyup.cli.cache.get_cache")
    def test_clear(self, mock_get_cache):
        """Test cache clear."""
        mock_cache = Mock()
        mock_get_cache.return_value = mock_cache

        clear_cache()

        mock_cache.clear.assert_called_once()

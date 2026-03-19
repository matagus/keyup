"""Tests for KeyUp! cache module."""

from pathlib import Path
from unittest.mock import Mock, patch

from keyup.cli.cache import (
    get_cache,
    get_teams_data,
    get_lists_data,
    get_tasks_data,
    invalidate_tasks_cache,
    clear_cache,
    TEAMS_TTL,
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

    @patch("keyup.cli.cache.diskcache.Cache")
    @patch("keyup.cli.cache.Path")
    def test_get_cache_returns_cache_instance(self, mock_path_class, mock_cache):
        """Test that get_cache returns a Cache instance."""
        mock_path_class.return_value = Mock()
        cache = get_cache()
        assert cache is mock_cache.return_value


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


class TestGetListsData:
    """Tests for get_lists_data function."""

    @patch("keyup.cli.cache.get_cache")
    def test_cache_hit(self, mock_get_cache):
        """Test cache hit returns cached data."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=True)
        mock_cache.get = Mock(return_value=["cached_list"])
        mock_get_cache.return_value = mock_cache

        mock_team = Mock(id="team-123")
        result = get_lists_data(mock_team)

        assert result == ["cached_list"]
        mock_cache.get.assert_called_once_with("lists:team-123")

    @patch("keyup.cli.cache.get_cache")
    def test_cache_miss(self, mock_get_cache):
        """Test cache miss fetches from API and caches."""
        mock_cache = Mock()
        mock_cache.__contains__ = Mock(return_value=False)
        mock_get_cache.return_value = mock_cache

        mock_team = Mock(id="team-123")
        mock_team.lists = ["api_list"]

        result = get_lists_data(mock_team)

        assert result == ["api_list"]
        mock_cache.set.assert_called_once_with("lists:team-123", ["api_list"], expire=LISTS_TTL)


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

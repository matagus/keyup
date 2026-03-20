"""Caching layer for KeyUp! CLI using sqlite3.

Provides TTL-based caching for ClickUp API responses to reduce API calls.
"""

import pickle
import sqlite3
import time
from pathlib import Path

# Cache location: ~/.keyup/cache/
CACHE_DIR = Path.home() / ".keyup" / "cache"
CACHE_FILE = CACHE_DIR / "keyup_cache.db"

# TTL values in seconds
TEAMS_TTL = 24 * 60 * 60  # 24 hours
LISTS_TTL = 24 * 60 * 60  # 24 hours
TASKS_TTL = 5 * 60  # 5 minutes


class SQLiteCache:
    """SQLite-backed cache with TTL support using pickle serialization."""

    def __init__(self, db_path: str):
        self._db_path = db_path
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key        TEXT PRIMARY KEY,
                    value      BLOB NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)

    def __contains__(self, key: str) -> bool:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT expires_at FROM cache WHERE key = ?", (key,)).fetchone()
        return row is not None and row[0] > time.time()

    def get(self, key: str):
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute("SELECT value, expires_at FROM cache WHERE key = ?", (key,)).fetchone()
            if row is None:
                return None
            if row[1] <= time.time():
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                return None
        return pickle.loads(row[0])  # noqa: S301 - local self-written cache

    def set(self, key: str, value, expire: int) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (key, pickle.dumps(value), time.time() + expire),
            )

    def delete(self, key: str) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def clear(self) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM cache")


def get_cache() -> SQLiteCache:
    """Get or create disk cache instance."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return SQLiteCache(str(CACHE_FILE))


def get_teams_data(clickup):
    """Get teams data from cache or fetch from API.

    Args:
        clickup: ClickUp client instance.

    Returns:
        List of team objects.
    """
    cache = get_cache()
    cache_key = "teams"

    if cache_key in cache:
        return cache.get(cache_key)  # type: ignore[no-any-return]

    teams = clickup.teams
    cache.set(cache_key, teams, expire=TEAMS_TTL)
    return teams


def get_lists_data(team):
    """Get lists data for a team from cache or fetch from API.

    Args:
        team: Team object.

    Returns:
        List of list objects.
    """
    cache = get_cache()
    cache_key = f"lists:{team.id}"

    if cache_key in cache:
        return cache.get(cache_key)  # type: ignore[no-any-return]

    lists = team.lists
    cache.set(cache_key, lists, expire=LISTS_TTL)
    return lists


def get_tasks_data(team, list_id: str):
    """Get tasks data for a list from cache or fetch from API.

    Args:
        team: Team object.
        list_id: ClickUp list ID.

    Returns:
        List of task objects.
    """
    cache = get_cache()
    cache_key = f"tasks:{list_id}"

    if cache_key in cache:
        return cache.get(cache_key)  # type: ignore[no-any-return]

    tasks = team.get_all_tasks(subtasks=False, list_ids=[list_id])
    cache.set(cache_key, tasks, expire=TASKS_TTL)
    return tasks


def invalidate_tasks_cache(list_id: str) -> None:
    """Invalidate cache for a specific list.

    Args:
        list_id: ClickUp list ID.
    """
    cache = get_cache()
    cache.delete(f"tasks:{list_id}")


def clear_cache() -> None:
    """Clear all cached data."""
    cache = get_cache()
    cache.clear()

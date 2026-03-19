"""Caching layer for KeyUp! CLI using diskcache.

Provides TTL-based caching for ClickUp API responses to reduce API calls.
"""

import os
from pathlib import Path

import diskcache

# Cache location: ~/.keyup/cache/
CACHE_DIR = Path.home() / ".keyup" / "cache"

# TTL values in seconds
TEAMS_TTL = 24 * 60 * 60  # 24 hours
SPACES_TTL = 24 * 60 * 60  # 24 hours
PROJECTS_TTL = 24 * 60 * 60  # 24 hours
LISTS_TTL = 24 * 60 * 60  # 24 hours
TASKS_TTL = 5 * 60  # 5 minutes


def get_cache() -> diskcache.Cache:
    """Get or create disk cache instance."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return diskcache.Cache(str(CACHE_DIR))


def get_teams_data(clickup) -> list:
    """Get teams data from cache or fetch from API.

    Args:
        clickup: ClickUp client instance.

    Returns:
        List of team objects.
    """
    cache = get_cache()
    cache_key = "teams"

    if cache_key in cache:
        return cache.get(cache_key)

    teams = clickup.teams
    cache.set(cache_key, teams, expire=TEAMS_TTL)
    return teams


def get_lists_data(team) -> list:
    """Get lists data for a team from cache or fetch from API.

    Args:
        team: Team object.

    Returns:
        List of list objects.
    """
    cache = get_cache()
    cache_key = f"lists:{team.id}"

    if cache_key in cache:
        return cache.get(cache_key)

    lists = team.lists
    cache.set(cache_key, lists, expire=LISTS_TTL)
    return lists


def get_tasks_data(team, list_id: str) -> list:
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
        return cache.get(cache_key)

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

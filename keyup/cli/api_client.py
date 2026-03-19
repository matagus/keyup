"""API client wrapper for ClickUp API interactions."""

import sys

import inquirer

from colorist import Color

from .exceptions import (
    TeamNotFoundError,
    TeamAmbiguousError,
    SpaceNotFoundError,
    ProjectNotFoundError,
    ListNotFoundError,
)


def get_team(clickup, argv):
    """Get team from CLI args or interactive selection.

    Args:
        clickup: ClickUp client instance.
        argv: Command line arguments.

    Returns:
        Team object.

    Raises:
        TeamNotFoundError: If team ID is invalid or no teams exist.
        TeamAmbiguousError: If multiple teams exist but no ID specified.
    """
    try:
        team_id = sys.argv[sys.argv.index("--team") + 1]
        return clickup.get_team_by_id(team_id)

    except ValueError:
        if len(clickup.teams) == 0:
            raise TeamNotFoundError()

        if len(clickup.teams) > 1:
            raise TeamAmbiguousError([t.name for t in clickup.teams])

        return clickup.teams[0]

    except Exception:
        # Invalid team ID provided
        raise TeamNotFoundError(team_id=argv[argv.index("--team") + 1] if "--team" in argv else None)


def get_space_for(team, argv):
    """Get space from CLI args or interactive selection.

    Args:
        team: Team object.
        argv: Command line arguments.

    Returns:
        Space object.

    Raises:
        SpaceNotFoundError: If space is not found.
    """
    try:
        space_id = sys.argv[sys.argv.index("--space") + 1]
        return team.get_space_by_id(space_id)

    except ValueError:
        if len(team.spaces) == 0:
            raise SpaceNotFoundError()

        if len(team.spaces) > 1:
            questions = [
                inquirer.List(
                    "space",
                    message=f"Select a {Color.CYAN}Space{Color.OFF}",
                    choices=[f"{space.name} [{space.id}]" for space in team.spaces],
                )
            ]

            answers = inquirer.prompt(questions)

            if answers:
                for space in team.spaces:
                    if f"{space.name} [{space.id}]" == answers["space"]:
                        return space

        return team.spaces[0]

    except Exception:
        # Invalid space ID provided
        raise SpaceNotFoundError(space_id=argv[argv.index("--space") + 1] if "--space" in argv else None)


def get_project_for(space, argv):
    """Get project from CLI args or interactive selection.

    Args:
        space: Space object.
        argv: Command line arguments.

    Returns:
        Project object.

    Raises:
        ProjectNotFoundError: If project is not found.
    """
    try:
        project_id = sys.argv[sys.argv.index("--project") + 1]
        return space.get_project_by_id(project_id)

    except ValueError:
        if len(space.projects) == 0:
            raise ProjectNotFoundError()

        if len(space.projects) > 1:
            questions = [
                inquirer.List(
                    "project",
                    message=f"Select a {Color.GREEN}Project{Color.OFF}",
                    choices=[f"{project.name} [{project.id}]" for project in space.projects],
                )
            ]

            answers = inquirer.prompt(questions)

            if answers:
                for project in space.projects:
                    if f"{project.name} [{project.id}]" == answers["project"]:
                        return project

        return space.projects[0]

    except Exception:
        # Invalid project ID provided
        raise ProjectNotFoundError(project_id=argv[argv.index("--project") + 1] if "--project" in argv else None)


def get_list_for(space_obj, argv):
    """Get list from CLI args or interactive selection.

    Args:
        space_obj: Space object.
        argv: Command line arguments.

    Returns:
        List object.

    Raises:
        ListNotFoundError: If list is not found.
    """
    try:
        index = sys.argv.index("--list")
        list_id = sys.argv[index + 1]
        return space_obj.get_list_by_id(list_id)

    except ValueError:
        if len(space_obj.lists) == 0:
            raise ListNotFoundError()

        if len(space_obj.lists) > 1:
            questions = [
                inquirer.List(
                    "list",
                    message=f"Select a {Color.YELLOW}List{Color.OFF}",
                    choices=[f"{li.name} [{li.id}]" for li in space_obj.lists],
                )
            ]

            answers = inquirer.prompt(questions)

            if answers:
                for li in space_obj.lists:
                    if f"{li.name} [{li.id}]" == answers["list"]:
                        return li

        return space_obj.lists[0]

    except Exception:
        # Invalid list ID provided
        raise ListNotFoundError(list_id=argv[argv.index("--list") + 1] if "--list" in argv else None)


def get_current_sprint_list(team, space):
    """Auto-detect current sprint list from team's lists.

    Searches for lists containing "sprint" or "iteration" in the name (case-insensitive).
    Sorts candidates by ID descending (most recent first) and returns the first match.

    Args:
        team: Team object.
        space: Space object (used to filter lists by space).

    Returns:
        List object for the current sprint.

    Raises:
        ListNotFoundError: If no sprint lists are found.
    """
    # Get all lists for the team
    all_lists = team.lists

    # Filter by space if provided
    if space:
        all_lists = [li for li in all_lists if li.space_id == space.id]

    # Find sprint/iteration lists
    sprint_lists = [li for li in all_lists if "sprint" in li.name.lower() or "iteration" in li.name.lower()]

    if not sprint_lists:
        raise ListNotFoundError(hint="No lists found with 'sprint' or 'iteration' in the name")

    # Sort by ID descending (most recent first)
    sprint_lists.sort(key=lambda x: x.id, reverse=True)

    return sprint_lists[0]

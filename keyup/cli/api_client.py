"""API client wrapper for ClickUp API interactions."""

import sys

import inquirer

from colorist import Color

from .exceptions import NoTeamFoundError, NoSpaceFoundError, NoProjectFoundError, NoListFoundError


def get_team(clickup, argv):
    """Get team from CLI args or interactive selection.

    Args:
        clickup: ClickUp client instance.
        argv: Command line arguments.

    Returns:
        Team object.

    Raises:
        NoTeamFoundError: If no team is found.
    """
    try:
        team_id = sys.argv[sys.argv.index("--team") + 1]
        return clickup.get_team_by_id(team_id)

    except ValueError:
        if len(clickup.teams) > 1:
            questions = [
                inquirer.List(
                    "team",
                    message=f"Select a {Color.MAGENTA}Team{Color.OFF}",
                    choices=[f"{team.name} [{team.id}]" for team in clickup.teams],
                )
            ]

            answers = inquirer.prompt(questions)

            if answers:
                for team in clickup.teams:
                    if f"{team.name} [{team.id}]" == answers["team"]:
                        return team

        elif len(clickup.teams) == 1:
            return clickup.teams[0]

    raise NoTeamFoundError()


def get_space_for(team, argv):
    """Get space from CLI args or interactive selection.

    Args:
        team: Team object.
        argv: Command line arguments.

    Returns:
        Space object.

    Raises:
        NoSpaceFoundError: If no space is found.
    """
    try:
        space_id = sys.argv[sys.argv.index("--space") + 1]
        return team.get_space_by_id(space_id)

    except ValueError:
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

        elif len(team.spaces) == 1:
            return team.spaces[0]

    raise NoSpaceFoundError()


def get_project_for(space, argv):
    """Get project from CLI args or interactive selection.

    Args:
        space: Space object.
        argv: Command line arguments.

    Returns:
        Project object.

    Raises:
        NoProjectFoundError: If no project is found.
    """
    try:
        project_id = sys.argv[sys.argv.index("--project") + 1]
        return space.get_project_by_id(project_id)

    except ValueError:
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

        elif len(space.projects) == 1:
            return space.projects[0]

    raise NoProjectFoundError()


def get_list_for(space_obj, argv):
    """Get list from CLI args or interactive selection.

    Args:
        space_obj: Space object.
        argv: Command line arguments.

    Returns:
        List object.

    Raises:
        NoListFoundError: If no list is found.
    """
    try:
        index = sys.argv.index("--list")
        list_id = sys.argv[index + 1]
        return space_obj.get_list_by_id(list_id)

    except ValueError:
        if len(space_obj.lists) == 1:
            return space_obj.lists[0]

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

    raise NoListFoundError()

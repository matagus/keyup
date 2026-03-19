"""Main CLI entry point for KeyUp!"""

import sys

from pyclickup import ClickUp

from .config import init_environ
from .api_client import get_team, get_space_for, get_project_for, get_list_for
from .renderer import render_list
from .exceptions import (
    NoTeamFoundError,
    NoSpaceFoundError,
    NoProjectFoundError,
    NoListFoundError,
)


def run_app():
    """Run the KeyUp! CLI application."""
    environ = init_environ()
    clickup = ClickUp(environ["TOKEN"])

    try:
        team_obj = get_team(clickup, sys.argv)
        space_obj = get_space_for(team_obj, sys.argv)
        project_obj = get_project_for(space_obj, sys.argv)
        list_obj = get_list_for(project_obj, sys.argv)
        render_list(list_obj, team_obj)

    except (NoTeamFoundError, NoSpaceFoundError, NoProjectFoundError, NoListFoundError) as e:
        print(e)
        sys.exit(1)

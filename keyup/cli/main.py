"""Main CLI entry point for KeyUp! using cyclopts."""

from typing import Annotated

from pyclickup import ClickUp
from cyclopts import App, Parameter

from .config import init_environ
from .api_client import get_team, get_space_for, get_project_for, get_list_for
from .renderer import render_list
from .exceptions import TokenError, handle_exception

app = App(name="keyup", help="A simple and beautiful console-based client for ClickUp.")


@app.default
def list_tasks(
    team: Annotated[str | None, Parameter(name="--team", help="Team ID")] = None,
    space: Annotated[str | None, Parameter(name="--space", help="Space ID")] = None,
    project: Annotated[str | None, Parameter(name="--project", help="Project ID")] = None,
    list_id: Annotated[str | None, Parameter(name="--list", help="List ID")] = None,
) -> None:
    """List tasks from a ClickUp list.

    Navigates through Team -> Space -> Project -> List hierarchy
    and displays all tasks grouped by status.
    """
    environ = init_environ()
    token = environ.get("TOKEN")
    if not token:
        raise TokenError()

    clickup = ClickUp(token)

    # Build argv-style list for backward compatibility with api_client
    argv = []
    if team:
        argv.extend(["--team", team])
    if space:
        argv.extend(["--space", space])
    if project:
        argv.extend(["--project", project])
    if list_id:
        argv.extend(["--list", list_id])

    team_obj = get_team(clickup, argv)
    space_obj = get_space_for(team_obj, argv)
    project_obj = get_project_for(space_obj, argv)
    list_obj = get_list_for(project_obj, argv)
    render_list(list_obj, team_obj)


def run_app():
    """Run the KeyUp! CLI application."""
    from .exceptions import ClickupyError

    try:
        app()
    except ClickupyError as e:
        handle_exception(e)

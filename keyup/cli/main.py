"""Main CLI entry point for KeyUp! using cyclopts."""

from typing import Annotated

from pyclickup import ClickUp
from cyclopts import App, Parameter

from .config import init_environ
from .api_client import get_team, get_space_for, get_project_for, get_list_for, get_current_sprint_list
from .renderer import render_list, render_task_detail, render_task_update
from .exceptions import TokenError, handle_exception

app = App(name="keyup", help="A simple and beautiful console-based client for ClickUp.")


@app.default
def list_tasks(
    team: Annotated[str | None, Parameter(name="--team", help="Team ID")] = None,
    space: Annotated[str | None, Parameter(name="--space", help="Space ID")] = None,
    project: Annotated[str | None, Parameter(name="--project", help="Project ID")] = None,
    list_id: Annotated[str | None, Parameter(name="--list", help="List ID")] = None,
    assignee: Annotated[str | None, Parameter(name="--assignee", help="Filter by assignee username")] = None,
    priority: Annotated[
        str | None, Parameter(name="--priority", help="Filter by priority (low, normal, high, urgent)")
    ] = None,
    due_before: Annotated[
        str | None, Parameter(name="--due-before", help="Filter tasks due before date (YYYY-MM-DD)")
    ] = None,
    group_by: Annotated[
        str, Parameter(name="--group-by", help="Group by: status (default), assignee, priority")
    ] = "status",
    no_cache: Annotated[bool, Parameter(name="--no-cache", help="Bypass cache")] = False,
    interactive: Annotated[bool, Parameter(name="-i", help="Enable interactive mode")] = False,
) -> None:
    """List tasks from a ClickUp list.

    Navigates through Team -> Space -> Project -> List hierarchy
    and displays all tasks grouped by status.

    Filters:
        --assignee: Filter by assignee username (case-insensitive)
        --priority: Filter by priority level (low, normal, high, urgent)
        --due-before: Filter tasks due before date (YYYY-MM-DD)

    Grouping:
        --group-by: Group by status (default), assignee, or priority

    Interactive Mode:
        -i, --interactive: Prompt for Team/Space/Project/List selection
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

    team_obj = get_team(clickup, argv, interactive=interactive)
    space_obj = get_space_for(team_obj, argv, interactive=interactive)
    project_obj = get_project_for(space_obj, argv, interactive=interactive)
    list_obj = get_list_for(project_obj, argv, interactive=interactive)
    render_list(
        list_obj,
        team_obj,
        no_cache=no_cache,
        assignee=assignee,
        priority=priority,
        due_before=due_before,
        group_by=group_by,
    )


def run_app():
    """Run the KeyUp! CLI application."""
    from .exceptions import ClickupyError

    try:
        app()
    except ClickupyError as e:
        handle_exception(e)


@app.command
def sprint(
    team: Annotated[str | None, Parameter(name="--team", help="Team ID")] = None,
    space: Annotated[str | None, Parameter(name="--space", help="Space ID")] = None,
    project: Annotated[str | None, Parameter(name="--project", help="Project ID")] = None,
    assignee: Annotated[str | None, Parameter(name="--assignee", help="Filter by assignee username")] = None,
    priority: Annotated[
        str | None, Parameter(name="--priority", help="Filter by priority (low, normal, high, urgent)")
    ] = None,
    due_before: Annotated[
        str | None, Parameter(name="--due-before", help="Filter tasks due before date (YYYY-MM-DD)")
    ] = None,
    group_by: Annotated[
        str, Parameter(name="--group-by", help="Group by: status (default), assignee, priority")
    ] = "status",
    no_cache: Annotated[bool, Parameter(name="--no-cache", help="Bypass cache")] = False,
    interactive: Annotated[bool, Parameter(name="-i", help="Enable interactive mode")] = False,
) -> None:
    """List tasks from the current sprint.

    Auto-detects the current sprint list by searching for lists
    containing "sprint" or "iteration" in the name.

    Filters:
        --assignee: Filter by assignee username (case-insensitive)
        --priority: Filter by priority level (low, normal, high, urgent)
        --due-before: Filter tasks due before date (YYYY-MM-DD)

    Grouping:
        --group-by: Group by status (default), assignee, or priority

    Interactive Mode:
        -i, --interactive: Prompt for Team/Space/Project selection
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

    team_obj = get_team(clickup, argv, interactive=interactive)
    space_obj = get_space_for(team_obj, argv, interactive=interactive)
    _ = get_project_for(space_obj, argv, interactive=interactive)  # Navigate to project but don't use it

    # Auto-detect sprint list
    list_obj = get_current_sprint_list(team_obj, space_obj)

    render_list(
        list_obj,
        team_obj,
        no_cache=no_cache,
        assignee=assignee,
        priority=priority,
        due_before=due_before,
        group_by=group_by,
    )


@app.command(name="task")
def show_task(
    task_id: Annotated[str, Parameter(name="task_id", help="Task ID")],
    team: Annotated[str | None, Parameter(name="--team", help="Team ID")] = None,
    interactive: Annotated[bool, Parameter(name="-i", help="Enable interactive mode")] = False,
) -> None:
    """Show detailed information about a specific task.

    Displays all task metadata including ID, name, status, URL,
    assignees, priority, due date, description, and subtasks.

    Args:
        task_id: ClickUp task ID.
        team: Optional team ID (required if multiple teams exist).
        interactive: Enable interactive team selection.
    """
    environ = init_environ()
    token = environ.get("TOKEN")
    if not token:
        raise TokenError()

    clickup = ClickUp(token)

    # Build argv for team resolution
    argv = []
    if team:
        argv.extend(["--team", team])

    get_team(clickup, argv, interactive=interactive)

    # Get task by ID
    task = clickup.get_task_by_id(task_id)  # type: ignore[attr-defined]

    render_task_detail(task)


@app.command(name="update")
def update_task(
    task_id: Annotated[str, Parameter(name="task_id", help="Task ID")],
    status: Annotated[str, Parameter(name="--status", help="New status name")],
    team: Annotated[str | None, Parameter(name="--team", help="Team ID")] = None,
    interactive: Annotated[bool, Parameter(name="-i", help="Enable interactive mode")] = False,
) -> None:
    """Update the status of a specific task.

    Changes the task status to the specified value.
    Shows confirmation with old -> new status transition.

    Args:
        task_id: ClickUp task ID.
        status: New status name (e.g., "To Do", "In Progress", "Done").
        team: Optional team ID (required if multiple teams exist).
        interactive: Enable interactive team selection.
    """
    environ = init_environ()
    token = environ.get("TOKEN")
    if not token:
        raise TokenError()

    clickup = ClickUp(token)

    # Build argv for team resolution
    argv = []
    if team:
        argv.extend(["--team", team])

    get_team(clickup, argv, interactive=interactive)

    # Get current task to find old status
    task = clickup.get_task_by_id(task_id)  # type: ignore[attr-defined]
    old_status = task.status.status

    # Update task status
    clickup.update_task(task_id, status=status)  # type: ignore[attr-defined]

    render_task_update(task_id, old_status, status)

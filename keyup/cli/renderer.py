"""Terminal output rendering for KeyUp! CLI."""

from collections import defaultdict
from datetime import datetime

from colorist import Effect, Color, ColorHex, BgColorHex

from .cache import get_tasks_data


def _filter_tasks(task_list, assignee=None, priority=None, due_before=None):
    """Filter tasks based on criteria.

    Args:
        task_list: List of task objects.
        assignee: Filter by assignee username (case-insensitive).
        priority: Filter by priority level (low, normal, high, urgent).
        due_before: Filter tasks due before date (YYYY-MM-DD).

    Returns:
        Filtered list of tasks.
    """
    filtered = task_list

    if assignee:
        assignee_lower = assignee.lower()
        filtered = [t for t in filtered if any(a.username.lower() == assignee_lower for a in t.assignees)]

    if priority:
        priority_map = {"low": 1, "normal": 2, "high": 3, "urgent": 4}
        priority_value = priority_map.get(priority.lower())
        if priority_value:
            filtered = [t for t in filtered if t.priority and t.priority.get("priority") == priority.lower()]

    if due_before:
        try:
            due_date = datetime.strptime(due_before, "%Y-%m-%d")
            filtered = [
                t for t in filtered if t.due_date and datetime.strptime(t.due_date, "%Y-%m-%dT%H:%M:%S.%fZ") < due_date
            ]
        except ValueError:
            pass  # Invalid date format, skip filtering

    return filtered


def render_list(list_obj, team_obj, no_cache: bool = False, assignee=None, priority=None, due_before=None):
    """Render tasks from a list grouped by status.

    Args:
        list_obj: List object from ClickUp.
        team_obj: Team object from ClickUp.
        no_cache: If True, bypass cache and fetch from API.
        assignee: Filter by assignee username (case-insensitive).
        priority: Filter by priority level (low, normal, high, urgent).
        due_before: Filter tasks due before date (YYYY-MM-DD).
    """
    # Print a header with the list and team names
    styled_list_name = f"{Color.YELLOW}{Effect.BOLD}{list_obj.name}{Effect.BOLD_OFF}{Color.OFF}"
    team_name = f"{Effect.BOLD}{Color.MAGENTA}{team_obj.name}{Color.OFF}{Effect.BOLD_OFF}"

    # Build filter info for header
    filters = []
    if assignee:
        filters.append(f"assignee={assignee}")
    if priority:
        filters.append(f"priority={priority}")
    if due_before:
        filters.append(f"due_before={due_before}")

    filter_info = f" [{', '.join(filters)}]" if filters else ""
    print(f"{styled_list_name} :: Team: {team_name}{filter_info}")

    if no_cache:
        task_list = team_obj.get_all_tasks(subtasks=False, list_ids=[list_obj.id])
    else:
        task_list = get_tasks_data(team_obj, list_obj.id)

    # Apply filters
    task_list = _filter_tasks(task_list, assignee=assignee, priority=priority, due_before=due_before)

    tasks_by_status = defaultdict(list)
    color_for_status = {}
    color_order = {}

    for task in task_list:
        # ignore print subtasks...
        if task.parent is None:
            tasks_by_status[task.status.status].append(task)
            color_for_status[task.status.status] = task.status.color
            color_order[task.status.status] = task.status.orderindex

    ordered_statuses = list(tasks_by_status.keys())
    ordered_statuses.sort(key=lambda x: color_order[x])

    for status_name in ordered_statuses:
        task_list = tasks_by_status[status_name]
        status_color = BgColorHex(color_for_status[status_name])
        print(f"\n{status_color} {status_name.upper()} {status_color.OFF} \n")

        for task in task_list:
            task_name = f"{Effect.BOLD}{task.name}{Effect.BOLD_OFF}"
            task_url = f"{Color.BLUE}{Effect.UNDERLINE}{task.url}{Effect.UNDERLINE_OFF}{Color.OFF}"
            task_assinees = ", ".join([f"{a.username}" for a in task.assignees])
            task_assignees = f"{Color.BLACK}({task_assinees}){Color.OFF}" if task_assinees else ""

            task_priority = ""
            if task.priority is not None:
                priority_color = ColorHex(task.priority["color"])
                priority_label = task.priority["priority"].capitalize()
                task_priority = f"[{priority_color}{priority_label}{priority_color.OFF}] "

            print(f" ▫ {task_priority}{task_name}: {task_url} {task_assignees}")

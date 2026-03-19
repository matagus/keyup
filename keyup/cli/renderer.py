"""Terminal output rendering for KeyUp! CLI."""

from collections import defaultdict

from colorist import Effect, Color, ColorHex, BgColorHex


def render_list(list_obj, team_obj):
    """Render tasks from a list grouped by status.

    Args:
        list_obj: List object from ClickUp.
        team_obj: Team object from ClickUp.
    """
    # Print a header with the list and team names
    styled_list_name = f"{Color.YELLOW}{Effect.BOLD}{list_obj.name}{Effect.BOLD_OFF}{Color.OFF}"
    team_name = f"{Effect.BOLD}{Color.MAGENTA}{team_obj.name}{Color.OFF}{Effect.BOLD_OFF}"
    print(f"{styled_list_name} :: Team: {team_name}")

    task_list = team_obj.get_all_tasks(subtasks=False, list_ids=[list_obj.id])

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

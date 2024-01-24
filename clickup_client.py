import sys

from collections import defaultdict

import dotenv

from colorist import Effect, Color, ColorHex, BgColorHex
from pyclickup import ClickUp


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    environ = dotenv.dotenv_values()

    clickup = ClickUp(environ["TOKEN"])

    try:
        team_id = sys.argv[sys.argv.index("--team") + 1]
        team = clickup.get_team_by_id(team_id)
    except ValueError:
        if len(clickup.teams) > 1:
            print("Multiple teams found, please specify which one to use:")
            for team in clickup.teams:
                print(f"  ▢ [{team.id}] {team.name}")

            print("Usage: python clickup_client.py [--team <team_id>] --list <list_id>")
            sys.exit(1)

        elif len(clickup.teams) == 1:
            team = clickup.teams[0]

        else:
            print("No teams found, please create one first.")
            sys.exit(1)

    try:
        index = sys.argv.index("--list")
        list_id = sys.argv[index + 1]
    except ValueError:
        for space in team.spaces:
            print(f"Space: {space.name}")

            for project in space.projects:
                print(f"  ▢ Project: {project.name}")

                for li in project.lists:
                    print(f"    ▫ [{li.id}] {li.name}")

        print("\n\nUsage: python clickup_client.py [--team <team_id>] --list <list_id>")
        sys.exit(0)


    all_lists_by_id = {}
    for space in team.spaces:
        for project in space.projects:
            for li in project.lists:
                all_lists_by_id[li.id] = li.name

    # Print a header with the list and team names
    list_name = all_lists_by_id[list_id]
    styled_list_name = f"{Color.YELLOW}{Effect.BOLD}{list_name}{Effect.BOLD_OFF}{Color.OFF}"
    team_name = f"{Effect.BOLD}{Color.MAGENTA}{team.name}{Color.OFF}{Effect.BOLD_OFF}"
    print(f"{styled_list_name} :: Team: {team_name}")

    task_list = team.get_all_tasks(subtasks=False, list_ids=[list_id])

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

            task_priority = ""
            if task.priority is not None:
                priority_color = ColorHex(task.priority["color"])
                priority_label = task.priority["priority"].capitalize()
                task_priority = f"({priority_color}{priority_label}{priority_color.OFF}) "

            print(f" ▫ {task_priority}{task_name}: {task_url}")

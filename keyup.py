import sys

from collections import defaultdict

import dotenv
import inquirer

from colorist import Effect, Color, ColorHex, BgColorHex
from pyclickup import ClickUp


def  init_environ():
    dotenv.load_dotenv(".env")
    return dotenv.dotenv_values()


class NoTeamFoundError(Exception):
    def __init__(self):
        super().__init__("No team found. Please create at least one team.")


class NoSpaceFoundError(Exception):
    def __init__(self):
        super().__init__("No space found. Please create at least one space for this team.")


class NoProjectFoundError(Exception):
    def __init__(self):
        super().__init__("No project found. Please create at least one project for this space.")


class NoListFoundError(Exception):
    def __init__(self):
        super().__init__("No list found. Please create at least one list for this project.")


def get_team(clickup, argv):
    try:
        team_id = sys.argv[sys.argv.index("--team") + 1]
        return clickup.get_team_by_id(team_id)

    except ValueError:
        if len(clickup.teams) > 1:
            questions = [
                inquirer.List(
                    "team", message=f"Select a {Color.MAGENTA}Team{Color.OFF}",
                    choices=[f"{team.name} [{team.id}]" for team in clickup.teams],
                )
            ]

            answers = inquirer.prompt(questions)

            for team in clickup.teams:
                if f"{team.name} [{team.id}]" == answers["team"]:
                    return team

        elif len(clickup.teams) == 1:
            return clickup.teams[0]

    raise NoTeamFoundError()


def get_list_for(space_obj, argv):
    try:
        index = sys.argv.index("--list")
        list_id = sys.argv[index + 1]
        return space_obj.get_list_by_id(list_id)

    except ValueError:
        if len(space_obj.lists) == 1:
            return space_obj.lists[0]

        questions = [
            inquirer.List(
                "list", message=f"Select a {Color.YELLOW}List{Color.OFF}",
                choices=[f"{li.name} [{li.id}]" for li in space_obj.lists],
            )
        ]

        answers = inquirer.prompt(questions)

        for li in space_obj.lists:
            if f"{li.name} [{li.id}]" == answers["list"]:
                return li

    raise NoListFoundError()


def get_space_for(team, argv):
    try:
        space_id = sys.argv[sys.argv.index("--space") + 1]
        return team.get_space_by_id(space_id)

    except ValueError:
        if len(team.spaces) > 1:
            questions = [
                inquirer.List(
                    "space", message=f"Select a {Color.CYAN}Space{Color.OFF}",
                    choices=[f"{space.name} [{space.id}]" for space in team.spaces],
                )
            ]

            answers = inquirer.prompt(questions)

            for space in team.spaces:
                if f"{space.name} [{space.id}]" == answers["space"]:
                    return space

        elif len(team.spaces) == 1:
            return team.spaces[0]

    raise NoSpaceFoundError()


def get_project_for(space, argv):
    try:
        project_id = sys.argv[sys.argv.index("--project") + 1]
        return space.get_project_by_id(project_id)

    except ValueError:
        if len(space.projects) > 1:
            questions = [
                inquirer.List(
                    "project", message=f"Select a {Color.GREEN}Project{Color.OFF}",
                    choices=[f"{project.name} [{project.id}]" for project in space.projects],
                )
            ]

            answers = inquirer.prompt(questions)

            for project in space.projects:
                if f"{project.name} [{project.id}]" == answers["project"]:
                    return project

        elif len(space.projects) == 1:
            return space.projects[0]

    raise NoProjectFoundError()


def render_list(list_obj, team_obj):
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


if __name__ == "__main__":
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

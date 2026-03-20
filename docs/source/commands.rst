Commands Reference
==================

This page documents all available KeyUp! CLI commands and their options.

``keyup`` (default) - List Tasks
--------------------------------

List all tasks from a ClickUp list, grouped by status.

Synopsis
~~~~~~~~

.. code-block:: bash

   keyup [OPTIONS]

Options
~~~~~~~

.. option:: --team

   Team ID (required when multiple teams exist)

.. option:: --space

   Space ID

.. option:: --project

   Project ID

.. option:: --list

   List ID

.. option:: --assignee

   Filter by assignee username (case-insensitive)

.. option:: --priority

   Filter by priority (low, normal, high, urgent)

.. option:: --due-before

   Filter tasks due before date (YYYY-MM-DD)

.. option:: --group-by

   Group by status (default), assignee, or priority

.. option:: --no-cache

   Bypass cache and fetch from API

.. option:: -i, --interactive

   Enable interactive mode for Team/Space/Project/List selection

Examples
~~~~~~~~

Basic usage:

.. code-block:: bash

   keyup --team 12345 --list 67890

Filter by assignee and priority:

.. code-block:: bash

   keyup --team 12345 --list 67890 --assignee john --priority high

Group by assignee:

.. code-block:: bash

   keyup --team 12345 --list 67890 --group-by assignee

Interactive mode:

.. code-block:: bash

   keyup -i

Bypass cache:

.. code-block:: bash

   keyup --team 12345 --list 67890 --no-cache

``keyup sprint`` - Current Sprint Tasks
---------------------------------------

Auto-detects the current sprint list by searching for lists containing "sprint" or "iteration" in the name.

Synopsis
~~~~~~~~

.. code-block:: bash

   keyup sprint [OPTIONS]

Options
~~~~~~~

Same options as ``keyup`` command, except ``--list`` is not needed (auto-detected).

Examples
~~~~~~~~

List tasks from current sprint:

.. code-block:: bash

   keyup sprint --team 12345

Filter sprint tasks by assignee:

.. code-block:: bash

   keyup sprint --team 12345 --assignee jane

Group sprint tasks by priority:

.. code-block:: bash

   keyup sprint --team 12345 --group-by priority

``keyup task`` - Task Details
-----------------------------

Show detailed information about a specific task.

Synopsis
~~~~~~~~

.. code-block:: bash

   keyup task <task_id> [OPTIONS]

Arguments
~~~~~~~~~

.. option:: task_id

   ClickUp task ID

Options
~~~~~~~

.. option:: --team

   Team ID (required if multiple teams exist)

.. option:: -i, --interactive

   Enable interactive mode

Examples
~~~~~~~~

Show task details:

.. code-block:: bash

   keyup task 123456

With team specification:

.. code-block:: bash

   keyup task 123456 --team 12345

``keyup update`` - Update Task Status
-------------------------------------

Update the status of a specific task.

Synopsis
~~~~~~~~

.. code-block:: bash

   keyup update <task_id> [OPTIONS]

Arguments
~~~~~~~~~

.. option:: task_id

   ClickUp task ID

Options
~~~~~~~

.. option:: --status

   New status name (e.g., "To Do", "In Progress", "Done")

.. option:: --team

   Team ID (required if multiple teams exist)

.. option:: -i, --interactive

   Enable interactive mode

Examples
~~~~~~~~

Update task status:

.. code-block:: bash

   keyup update 123456 --status "In Progress"

With team specification:

.. code-block:: bash

   keyup update 123456 --status "Done" --team 12345

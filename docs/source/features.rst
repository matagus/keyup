Features
========

This page describes the key features of QuickUp!.

Task Listing
------------

QuickUp! displays tasks from ClickUp lists with:

- **Bold** task names
- Blue underlined URLs
- Color-coded priority badges
- Assignee names in parentheses
- Status groups with color-coded headers matching ClickUp status colors

Filtering
---------

Filter tasks by various criteria:

Assignee Filter
~~~~~~~~~~~~~~~

Filter tasks by assignee username (case-insensitive):

.. code-block:: bash

   quickup --team 123 --list 456 --assignee john

Priority Filter
~~~~~~~~~~~~~~~

Filter by priority level:

.. code-block:: bash

   quickup --team 123 --list 456 --priority high

Supported priorities: low, normal, high, urgent

Due Date Filter
~~~~~~~~~~~~~~~

Filter tasks due before a specific date:

.. code-block:: bash

   quickup --team 123 --list 456 --due-before 2024-12-31

Grouping
--------

Group tasks by different criteria:

.. code-block:: bash

   # Group by status (default)
   quickup --team 123 --list 456 --group-by status

   # Group by assignee
   quickup --team 123 --list 456 --group-by assignee

   # Group by priority
   quickup --team 123 --list 456 --group-by priority

Sprint Detection
----------------

The ``quickup sprint`` command auto-detects the current sprint by searching for lists containing "sprint" or "iteration" in the name:

.. code-block:: bash

   quickup sprint --team 123

Interactive Mode
----------------

When multiple teams, spaces, projects, or lists exist, use the ``-i`` flag to enable interactive selection:

.. code-block:: bash

   quickup -i

This prompts you to select:

1. Team (if multiple teams exist)
2. Space (if multiple spaces exist)
3. Project (if multiple projects exist)
4. List (if multiple lists exist)

Caching
-------

QuickUp! uses disk-based caching to reduce API calls and improve performance:

- **Teams**: 24 hours TTL
- **Lists**: 24 hours TTL
- **Tasks**: 5 minutes TTL

Cache location: ``~/.quickup/cache/``

Bypass the cache with ``--no-cache``:

.. code-block:: bash

   quickup --team 123 --list 456 --no-cache

Output Format
-------------

Tasks are displayed with formatted output:

- Task name in **bold**
- Task URL in blue with underline
- Priority badge with color coding:
  - Urgent: Red
  - High: Orange
  - Normal: Blue
  - Low: Gray
- Assignee names in parentheses

Status groups are displayed with color-coded headers matching the ClickUp status colors.

At the bottom of the output, a suggestion is shown in gray text with the command to repeat the same query:

.. code-block:: text

   Run again: quickup --assignee john --priority high --group-by priority

This makes it easy to re-run the same filtered/grouped view without typing the full command again.

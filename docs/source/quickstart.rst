Quick Start
===========

This guide will help you get started with KeyUp! in just a few minutes.

Installation
------------

Install KeyUp! using pip:

.. code-block:: bash

   pip install keyup

Configuration
-------------

Set your ClickUp API token as an environment variable:

.. code-block:: bash

   export CLICKUP_TOKEN=your_token_here

Alternatively, create a ``.env`` file in your project directory:

.. code-block:: bash

   CLICKUP_TOKEN=your_token_here

Basic Usage
-----------

List all tasks from a specific ClickUp list:

.. code-block:: bash

   keyup --team <team_id> --list <list_id>

Use interactive mode to navigate through your workspace hierarchy:

.. code-block:: bash

   keyup -i

List tasks from the current sprint:

.. code-block:: bash

   keyup sprint --team <team_id>

View details of a specific task:

.. code-block:: bash

   keyup task <task_id>

Update a task's status:

.. code-block:: bash

   keyup update <task_id> --status "In Progress"

Next Steps
----------

- Read the :doc:`Installation` guide for detailed installation instructions
- Check the :doc:`commands` reference for all available CLI options
- Explore :doc:`features` to learn about filtering, grouping, and caching

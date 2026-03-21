QuickUp! Documentation
=====================

A simple, lightweight, and beautiful console-based client for ClickUp.

Quick Start
-----------

Install QuickUp!:

.. code-block:: bash

   pip install quickup

Configure your ClickUp API token:

.. code-block:: bash

   export CLICKUP_TOKEN=your_token_here

Run the tool:

.. code-block:: bash

   quickup --help

Feature Highlights
------------------

**CLI Commands**

- ``quickup`` - List tasks from a ClickUp list with color-coded status groups
- ``quickup sprint`` - Auto-detect and list tasks from the current sprint
- ``quickup task <id>`` - Show detailed information about a specific task
- ``quickup update <id>`` - Update a task's status

**Features**

- Task filtering by assignee, priority, or due date
- Task grouping by status, assignee, or priority
- Interactive mode for navigating Team → Space → Project → List hierarchy
- Disk-based caching for improved performance (24h for teams/lists, 5min for tasks)
- Color-coded output matching ClickUp status colors

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started:

   quickstart
   Installation

.. toctree::
   :maxdepth: 2
   :caption: User Guide:

   commands
   features

.. toctree::
   :maxdepth: 2
   :caption: Developer Guide:

   api
   troubleshooting
   contributing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

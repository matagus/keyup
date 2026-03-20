Troubleshooting
===============

This page covers common issues and their solutions.

Token Errors
------------

Problem: Token not found
~~~~~~~~~~~~~~~~~~~~~~~~

Error message: ``Token error``

Solution: Ensure your ClickUp API token is set correctly:

.. code-block:: bash

   export CLICKUP_TOKEN=your_token_here

Or create a ``.env`` file:

.. code-block:: bash

   CLICKUP_TOKEN=your_token_here

Verify the token is loaded:

.. code-block:: bash

   echo $CLICKUP_TOKEN

Team Errors
-----------

Problem: Team not found or ambiguous team
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exit code: 2

Solution: Specify the team ID explicitly:

.. code-block:: bash

   keyup --team <team_id> --list <list_id>

Or use interactive mode to select a team:

.. code-block:: bash

   keyup -i

List Errors
-----------

Problem: List not found
~~~~~~~~~~~~~~~~~~~~~~~

Exit code: 3

Solution: Verify the list ID is correct and exists in the specified space/project:

.. code-block:: bash

   keyup --team <team_id> --space <space_id> --list <list_id>

Network Errors
--------------

Problem: Network error
~~~~~~~~~~~~~~~~~~~~~~

Exit code: 4

Solution:

1. Check your internet connection
2. Verify the ClickUp API is accessible
3. Try again with ``--no-cache`` to bypass cached data

API Errors
----------

Problem: API error
~~~~~~~~~~~~~~~~~~

Exit code: 5

Solution:

1. Verify your API token is valid
2. Check ClickUp API status
3. Ensure you have proper permissions for the requested resources

Cache Issues
------------

Problem: Stale data
~~~~~~~~~~~~~~~~~~~

Solution: Use ``--no-cache`` to fetch fresh data:

.. code-block:: bash

   keyup --team <team_id> --list <list_id> --no-cache

Problem: Cache directory permission errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Solution: Check permissions on ``~/.keyup/cache/``:

.. code-block:: bash

   chmod 755 ~/.keyup/cache

Exit Codes Reference
--------------------

+------+----------------------------------+
| Code | Meaning                          |
+======+==================================+
| 1    | Token error or general error     |
+------+----------------------------------+
| 2    | Team not found or ambiguous team |
+------+----------------------------------+
| 3    | List not found                   |
+------+----------------------------------+
| 4    | Network error                    |
+------+----------------------------------+
| 5    | API error                        |
+------+----------------------------------+
| 99   | Unexpected error                 |
+------+----------------------------------+

Getting Help
------------

For additional support:

- Check the `GitHub Issues <https://github.com/matagus/keyup/issues>`_
- Review the `ClickUp API documentation <https://clickup.com/api>`_
- Verify your environment with ``keyup --help``

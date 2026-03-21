Installation
============

System Requirements
-------------------

- Python 3.10 or higher
- ClickUp API token
- pip or uv package manager

Installation Steps
------------------

1. Install from PyPI:

   .. code-block:: bash

      pip install quickup

2. Alternatively, install using uv:

   .. code-block:: bash

      uv pip install quickup

3. Verify the installation:

   .. code-block:: bash

      quickup --help

Configuration
-------------

After installation, you need to configure your ClickUp API token.

Option 1: Environment Variable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export the token in your shell:

.. code-block:: bash

   export CLICKUP_TOKEN=your_token_here

To make this permanent, add it to your shell configuration file (e.g., ``~/.bashrc``, ``~/.zshrc``):

.. code-block:: bash

   echo 'export CLICKUP_TOKEN=your_token_here' >> ~/.zshrc

Option 2: .env File
~~~~~~~~~~~~~~~~~~~

Create a ``.env`` file in your project directory:

.. code-block:: bash

   CLICKUP_TOKEN=your_token_here

QuickUp! will automatically load the token from this file.

Getting Your ClickUp API Token
------------------------------

1. Log in to your ClickUp account
2. Go to Settings → Apps → ClickUp API
3. Click on "Authorize"
4. Copy your API token
5. Store it securely

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade quickup

Uninstallation
--------------

To remove QuickUp!:

.. code-block:: bash

   pip uninstall quickup

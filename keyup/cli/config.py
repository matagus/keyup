"""Configuration and environment loading for KeyUp! CLI."""

import dotenv


def init_environ():
    """Load environment variables from .env file.

    Returns:
        dict: Environment variables as a dictionary.
    """
    dotenv.load_dotenv(".env")
    return dotenv.dotenv_values()

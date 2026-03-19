"""KeyUp! CLI - A simple and beautiful console-based client for ClickUp.

This module provides backward compatibility by re-exporting the main entry point.
The actual implementation is now in keyup.cli.main.
"""

from keyup.cli.main import run_app

if __name__ == "__main__":
    run_app()

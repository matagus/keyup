"""Custom exceptions for KeyUp! CLI."""


class NoTeamFoundError(Exception):
    """Raised when no team is found."""

    def __init__(self):
        super().__init__("No team found. Please create at least one team.")


class NoSpaceFoundError(Exception):
    """Raised when no space is found."""

    def __init__(self):
        super().__init__("No space found. Please create at least one space for this team.")


class NoProjectFoundError(Exception):
    """Raised when no project is found."""

    def __init__(self):
        super().__init__("No project found. Please create at least one project for this space.")


class NoListFoundError(Exception):
    """Raised when no list is found."""

    def __init__(self):
        super().__init__("No list found. Please create at least one list for this project.")

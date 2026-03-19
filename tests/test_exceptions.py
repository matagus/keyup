"""Tests for KeyUp! exceptions."""

from keyup.cli.exceptions import (
    NoTeamFoundError,
    NoSpaceFoundError,
    NoProjectFoundError,
    NoListFoundError,
)


class TestNoTeamFoundError:
    """Tests for NoTeamFoundError exception."""

    def test_message(self):
        """Test exception message."""
        exc = NoTeamFoundError()
        assert str(exc) == "No team found. Please create at least one team."


class TestNoSpaceFoundError:
    """Tests for NoSpaceFoundError exception."""

    def test_message(self):
        """Test exception message."""
        exc = NoSpaceFoundError()
        assert str(exc) == "No space found. Please create at least one space for this team."


class TestNoProjectFoundError:
    """Tests for NoProjectFoundError exception."""

    def test_message(self):
        """Test exception message."""
        exc = NoProjectFoundError()
        assert str(exc) == "No project found. Please create at least one project for this space."


class TestNoListFoundError:
    """Tests for NoListFoundError exception."""

    def test_message(self):
        """Test exception message."""
        exc = NoListFoundError()
        assert str(exc) == "No list found. Please create at least one list for this project."

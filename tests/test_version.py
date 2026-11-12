"""Tests for package version."""

from ad_copy_grader import __version__


def test_version() -> None:
    """Verify that package version matches expected release."""
    assert __version__ == "0.1.0"

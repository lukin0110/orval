"""Tests for the duration_utils module."""

import pytest
from typeguard import suppress_type_checks

from orval import pretty_duration


@pytest.mark.parametrize(
    ("seconds", "fmt", "expected"),
    [
        (9000, "s", "2h 30m"),
        (9000, "l", "2 hours 30 minutes"),
        (93784, "s", "1d 2h 3m 4s"),
        (93784, "l", "1 day 2 hours 3 minutes 4 seconds"),
        (3600, "s", "1h"),
        (3661, "l", "1 hour 1 minute 1 second"),
        (1.5, "s", "1s 500ms"),
        (1.5, "l", "1 second 500 milliseconds"),
        (0.25, "s", "250ms"),
        (0.000042, "s", "42µs"),
        (0.000001, "l", "1 microsecond"),
        (0.0000004, "s", "0s"),
        (0, "s", "0s"),
        (0, "l", "0 seconds"),
        (86400, "s", "1d"),
        (90000.0001, "s", "1d 1h 100µs"),
    ],
)
def test_format_duration(seconds: float, fmt: str, expected: str) -> None:
    """Should return a human-readable string representation of the duration."""
    assert pretty_duration(seconds, fmt) == expected


def test_format_duration_invalid_seconds() -> None:
    """Should raise a ValueError for a negative duration."""
    with pytest.raises(ValueError, match=r"Duration must be non-negative."):
        pretty_duration(-1)


def test_format_duration_invalid_format() -> None:
    """Should raise a ValueError for invalid format."""
    with pytest.raises(ValueError, match="Format must be one of"):
        pretty_duration(9000, "invalid-format")


@suppress_type_checks
def test_format_duration_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Duration must be a number."):
        pretty_duration("9000")  # ty: ignore[invalid-argument-type]

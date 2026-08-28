"""Tests for the duration_utils module."""

import pytest
from typeguard import suppress_type_checks

from orval import parse_duration, pretty_duration


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


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1h30m", 5400.0),
        ("2h 30m", 9000.0),
        ("2 hours 30 minutes", 9000.0),
        ("1d 2h 3m 4s", 93784.0),
        ("1 day 2 hours 3 minutes 4 seconds", 93784.0),
        ("1.5h", 5400.0),
        ("1s 500ms", 1.5),
        ("1 second 500 milliseconds", 1.5),
        ("250ms", 0.25),
        ("42µs", 0.000042),
        ("42us", 0.000042),
        ("42μs", 0.000042),  # Greek small letter mu.
        ("1 microsecond", 0.000001),
        ("90", 90.0),
        ("90.5", 90.5),
        ("0s", 0.0),
        ("0 seconds", 0.0),
        ("1 Hour", 3600.0),
        ("2 DAYS", 172800.0),
        ("  1h  30m  ", 5400.0),
        ("1e3 s", 1000.0),
        ("30m 1h", 5400.0),
    ],
)
def test_parse_duration(text: str, expected: float) -> None:
    """Should parse a human-readable duration string into seconds."""
    assert parse_duration(text) == expected


@pytest.mark.parametrize("seconds", [9000, 93784, 3600, 3661, 1.5, 0.25, 0.000042, 0.000001, 0, 86400, 90000.0001])
@pytest.mark.parametrize("fmt", ["s", "l"])
def test_parse_duration_round_trip(seconds: float, fmt: str) -> None:
    """Should invert pretty_duration for exactly-representable durations."""
    assert parse_duration(pretty_duration(seconds, fmt)) == seconds


@pytest.mark.parametrize("text", ["", "abc", "1..2", "h1", "1h 30", "1e309", "1e309h"])
def test_parse_duration_invalid_text(text: str) -> None:
    """Should raise a ValueError for unparseable text."""
    with pytest.raises(ValueError, match="Cannot parse"):
        parse_duration(text)


def test_parse_duration_negative() -> None:
    """Should raise a ValueError for a negative duration."""
    with pytest.raises(ValueError, match=r"Duration must be non-negative."):
        parse_duration("-1h")


def test_parse_duration_unknown_unit() -> None:
    """Should raise a ValueError for an unknown unit."""
    with pytest.raises(ValueError, match="Unknown duration unit"):
        parse_duration("1 fortnight")


@suppress_type_checks
def test_parse_duration_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Text must be a string."):
        parse_duration(5400)  # ty: ignore[invalid-argument-type]

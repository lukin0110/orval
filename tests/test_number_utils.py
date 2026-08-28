"""Tests for the number_utils module."""

import math

import pytest
from typeguard import suppress_type_checks

from orval import pretty_number


@pytest.mark.parametrize(
    ("value", "fmt", "precision", "expected"),
    [
        (0, "s", 1, "0"),
        (999, "s", 1, "999"),
        (1000, "s", 1, "1K"),
        (1234, "s", 1, "1.2K"),
        (1234567, "s", 1, "1.2M"),
        (1234567890, "s", 1, "1.2B"),
        (1234567890123, "s", 1, "1.2T"),
        (1234567890123456, "s", 1, "1234.6T"),
        (999950, "s", 1, "1M"),
        (999949, "s", 1, "999.9K"),
        (-1234567, "s", 1, "-1.2M"),
        (1234567, "s", 2, "1.23M"),
        (1234567, "s", 0, "1M"),
        (1500000, "s", 1, "1.5M"),
        (math.pi, "s", 1, "3.1"),
        (1234567, "l", 1, "1.2 million"),
        (1000, "l", 1, "1 thousand"),
        (999, "l", 1, "999"),
        (1234567890, "l", 1, "1.2 billion"),
        (1234567890123, "l", 1, "1.2 trillion"),
    ],
)
def test_pretty_number(value: float, fmt: str, precision: int, expected: str) -> None:
    """Should return a compact human-readable string representation of the number."""
    assert pretty_number(value, fmt, precision=precision) == expected


def test_pretty_number_invalid_format() -> None:
    """Should raise a ValueError for invalid format."""
    with pytest.raises(ValueError, match="Format must be one of"):
        pretty_number(1234567, "invalid-format")


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_pretty_number_non_finite(value: float) -> None:
    """Should raise a ValueError for a non-finite number."""
    with pytest.raises(ValueError, match=r"Value must be finite."):
        pretty_number(value)


@suppress_type_checks
def test_pretty_number_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Value must be a number."):
        pretty_number("1234567")  # ty: ignore[invalid-argument-type]

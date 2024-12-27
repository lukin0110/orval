"""Tests for the byte_utils module."""

import pytest
from typeguard import suppress_type_checks

from orval import pretty_bytes


@pytest.mark.parametrize(
    ("size", "fmt", "precision", "expected"),
    [
        (1024, "bs", 2, "1.00 KiB"),
        (1048576, "bs", 2, "1.00 MiB"),
        (1000, "ds", 2, "1.00 KB"),
        (1000000, "ds", 2, "1.00 MB"),
        (1024, "bs", 0, "1 KiB"),
        (1000, "ds", 0, "1 KB"),
        (1536, "bs", 2, "1.50 KiB"),
        (1536, "ds", 2, "1.54 KB"),
        (0, "bs", 2, "0.00 B"),
        (0, "ds", 2, "0.00 B"),
    ],
)
def test_format_bytes(size: int, fmt: str, precision: int, expected: str) -> None:
    """Should return a human-readable string representation of the size."""
    assert pretty_bytes(size, fmt, precision=precision) == expected


def test_format_bytes_invalid_size() -> None:
    """Should raise a ValueError for invalid size."""
    with pytest.raises(ValueError, match=r"Size must be a non-negative integer."):
        pretty_bytes(-1)


def test_format_bytes_invalid_format() -> None:
    """Should raise a ValueError for invalid format."""
    with pytest.raises(ValueError, match="Format must be one of"):
        pretty_bytes(1024, "invalid-format", precision=2)


@suppress_type_checks
def test_format_bytes_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Size must be an integer."):
        pretty_bytes("1024", precision=2)  # type: ignore[arg-type]

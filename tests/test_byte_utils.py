"""Tests for the byte_utils module."""

import pytest

from orval import format_bytes


@pytest.mark.parametrize(
    ("size", "fmt", "decimal_places", "expected"),
    [
        (1024, "binary", 2, "1.00 KiB"),
        (1048576, "binary", 2, "1.00 MiB"),
        (1000, "decimal", 2, "1.00 KB"),
        (1000000, "decimal", 2, "1.00 MB"),
        (1024, "binary", 0, "1 KiB"),
        (1000, "decimal", 0, "1 KB"),
        (1536, "binary", 2, "1.50 KiB"),
        (1536, "decimal", 2, "1.54 KB"),
        (0, "binary", 2, "0.00 B"),
        (0, "decimal", 2, "0.00 B"),
    ],
)
def test_format_bytes(size: int, fmt: str, decimal_places: int, expected: str) -> None:
    """Should return a human-readable string representation of the size."""
    assert format_bytes(size, fmt=fmt, decimal_places=decimal_places) == expected


def test_format_bytes_invalid_size() -> None:
    """Should raise a ValueError for invalid size."""
    with pytest.raises(ValueError, match="Size must be a non-negative integer."):
        format_bytes(-1)


def test_format_bytes_invalid_format() -> None:
    """Should raise a ValueError for invalid format."""
    with pytest.raises(ValueError, match="Format must be one of"):
        format_bytes(1024, fmt="invalid-format", decimal_places=2)

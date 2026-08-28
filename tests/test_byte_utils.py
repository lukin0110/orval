"""Tests for the byte_utils module."""

import pytest
from typeguard import suppress_type_checks

from orval import parse_bytes, pretty_bytes


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
        pretty_bytes("1024", precision=2)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1.5 GiB", 1610612736),
        ("1.00 KiB", 1024),
        ("1 KB", 1000),
        ("1.54 KB", 1540),
        ("512", 512),
        ("0 B", 0),
        ("20 Megabytes", 20000000),
        ("19 Mebibytes", 19922944),
        ("2 Kibibytes", 2048),
        ("1.5 gib", 1610612736),
        ("1.5 GIB", 1610612736),
        ("  1 kb  ", 1000),
        ("1e3 B", 1000),
        ("3.5MB", 3500000),
        ("9007199254740993", 9007199254740993),
        ("123456789012345678901 B", 123456789012345678901),
    ],
)
def test_parse_bytes(text: str, expected: int) -> None:
    """Should parse a human-readable size string into bytes."""
    assert parse_bytes(text) == expected


@pytest.mark.parametrize(
    ("size", "fmt"),
    [
        (1024, "bs"),
        (1536, "bs"),
        (1048576, "bs"),
        (1024, "bl"),
        (1000, "ds"),
        (20000000, "ds"),
        (20000000, "dl"),
        (0, "bs"),
    ],
)
def test_parse_bytes_round_trip(size: int, fmt: str) -> None:
    """Should invert pretty_bytes for exactly-representable sizes."""
    assert parse_bytes(pretty_bytes(size, fmt)) == size


@pytest.mark.parametrize("text", ["", "abc", "1..2", "KB 1", "1e309", "1e309 KB", "1e308 YB"])
def test_parse_bytes_invalid_text(text: str) -> None:
    """Should raise a ValueError for unparseable text."""
    with pytest.raises(ValueError, match="Cannot parse"):
        parse_bytes(text)


def test_parse_bytes_negative() -> None:
    """Should raise a ValueError for a negative size."""
    with pytest.raises(ValueError, match=r"Size must be non-negative."):
        parse_bytes("-1 KB")


def test_parse_bytes_unknown_unit() -> None:
    """Should raise a ValueError for an unknown unit."""
    with pytest.raises(ValueError, match="Unknown byte unit"):
        parse_bytes("1 XB")


@suppress_type_checks
def test_parse_bytes_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Text must be a string."):
        parse_bytes(1024)  # ty: ignore[invalid-argument-type]

"""Tests for chunkify function."""

from collections.abc import Iterable
from typing import Any

import pytest
from typeguard import suppress_type_checks

from orval import chunkify, flatten


@pytest.mark.parametrize(
    ("sequence", "size", "expected"),
    [
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),  # Normal case
        ([1, 2, 3], 5, [[1, 2, 3]]),  # Chunk size larger than list
        ([1, 2, 3, 4], 1, [[1], [2], [3], [4]]),  # Chunk size of 1
        ([1, 2, 3], 3, [[1, 2, 3]]),  # Chunk size equal to list length
        ({1, 2, 3}, 2, [[1, 2], [3]]),  # Set
        (range(5), 2, [[0, 1], [2, 3], [4]]),  # Range
        (("a", "b", "c"), 2, [["a", "b"], ["c"]]),  # Tuple
    ],
)
def test_chunkify(sequence: Iterable[Any], size: int, expected: list[list[Any]]) -> None:
    """Should return a list of chunks of the given size."""
    assert chunkify(sequence, size) == expected


@pytest.mark.parametrize("size", [-1, 0])
def test_chunkify_invalid_size(size: int) -> None:
    """Should raise a ValueError for invalid size."""
    with pytest.raises(ValueError, match=f"Size must be > 0, invalid value {size}"):
        chunkify([1, 2, 3], size)


@pytest.mark.parametrize(
    ("sequence", "depth", "expected"),
    [
        ([1, [2, [3, 4], 5]], None, [1, 2, 3, 4, 5]),
        ([1, [2, [3, 4], 5]], 1, [1, 2, [3, 4], 5]),
        ([1, [2, [3, 4], 5]], 2, [1, 2, 3, 4, 5]),
        ([1, [2, [3, 4], 5]], 0, [1, [2, [3, 4], 5]]),
        ({1}, None, [1]),
        ({1, 2}, None, [1, 2]),
        ([{1}, {2}], None, [1, 2]),
        ([{1, 2}], None, [1, 2]),
        ("", None, [""]),
        ("abc", None, ["abc"]),
        ([], None, []),
        (["a", ["b", "c"]], None, ["a", "b", "c"]),
    ],
)
def test_flatten(sequence: Iterable[Any] | set[Any], depth: int | None, expected: list[Any]) -> None:
    """Should return a flattened sequence up to the given depth."""
    assert list(flatten(sequence, depth)) == expected


def test_flatten_invalid_depth() -> None:
    """Should raise a ValueError for invalid depth."""
    with pytest.raises(ValueError, match="Depth must be >= 0, invalid value -1"):
        list(flatten([], -1))


@suppress_type_checks
def test_flatten_invalid_type() -> None:
    """Should raise a TypeError for invalid type."""
    with pytest.raises(TypeError, match=r"Input must be an interable \(list, set, range, tuple\)\."):
        list(flatten(1, 1))  # type: ignore[arg-type]

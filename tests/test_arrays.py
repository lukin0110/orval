"""Tests for chunkify function."""

import pytest

from orval import chunkify


@pytest.mark.parametrize(
    ("sequence", "size", "expected"),
    [
        ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),  # Normal case
        ([1, 2, 3], 5, [[1, 2, 3]]),  # Chunk size larger than list
        ([1, 2, 3, 4], 1, [[1], [2], [3], [4]]),  # Chunk size of 1
        ([1, 2, 3], 3, [[1, 2, 3]]),  # Chunk size equal to list length
    ],
)
def test_chunkify(sequence: list[int], size: int, expected: list[list[int]]) -> None:
    """Should return a list of chunks of the given size."""
    assert chunkify(sequence, size) == expected


def test_chunkify_invalid_size() -> None:
    """Should raise a ValueError for invalid size."""
    with pytest.raises(ValueError, match="Size must be > 0, invalid value 0"):
        chunkify([1, 2, 3], 0)

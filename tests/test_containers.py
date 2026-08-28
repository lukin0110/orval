"""Tests for container utilities."""

import re
from collections.abc import Iterable
from typing import Any

import pytest
from typeguard import suppress_type_checks

from orval import chunkify, deep_get, deep_merge, deep_set, flatten, omit, pick


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
        list(flatten(1, 1))  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("dicts", "expected"),
    [
        ([{"a": 1}, {"b": 2}], {"a": 1, "b": 2}),
        ([{"a": {"b": 1}}, {"a": {"c": 2}}], {"a": {"b": 1, "c": 2}}),
        ([{"a": 1}, {"a": {"b": 2}}], {"a": {"b": 2}}),
        ([{"a": {"b": 1}}, {"a": 2}], {"a": 2}),
        ([{"a": 1}, {"b": {"c": 2}}, {"b": {"d": 3}}], {"a": 1, "b": {"c": 2, "d": 3}}),
    ],
)
def test_deep_merge(dicts: list[dict[Any, Any]], expected: dict[Any, Any]) -> None:
    """Should return a deeply merged dictionary."""
    assert deep_merge(*dicts) == expected


@suppress_type_checks
@pytest.mark.parametrize(
    "invalid_input",
    [
        [1, {"a": 1}],
        [{"a": 1}, [2]],
    ],
)
def test_deep_merge_invalid_input(invalid_input: list[Any]) -> None:
    """Should raise a TypeError for invalid input."""
    with pytest.raises(TypeError, match=r"All inputs must be dictionaries."):
        deep_merge(*invalid_input)


@pytest.mark.parametrize(
    ("data", "path", "default", "expected"),
    [
        ({"a": 1, "b": 2}, "a", None, 1),  # Top-level key
        ({"a": {"b": {"c": 1}}}, "a.b.c", None, 1),  # Nested dict path
        ({"a": {"b": {"c": 1}}}, "a.b", None, {"c": 1}),  # Intermediate value
        ({"a": [{"b": 1}, {"b": 2}]}, "a[1].b", None, 2),  # List index
        ({"a": [10, 20, 30]}, "a[-1]", None, 30),  # Negative index
        ({"a": [[1, 2], [3]]}, "a[0][1]", None, 2),  # Chained indices
        ({"a": {"0": 1}}, "a.0", None, 1),  # Bare numeric segment is a dict key
        ({"a": {0: 1}}, "a[0]", None, 1),  # Bracket index resolves an integer dict key, like pick output
        ({"a": {"b": None}}, "a.b", 42, None),  # Explicit None beats the default
        ({"a": {"b": 1}}, "a.x", None, None),  # Missing key -> default None
        ({"a": {"b": 1}}, "a.x", 42, 42),  # Missing key -> custom default
        ({"a": [1]}, "a[5]", "nope", "nope"),  # Index out of range -> default
        ({"a": 1}, "a.b", 0, 0),  # Non-dict intermediate -> default
        ({"a": (1, 2)}, "a[0]", 0, 0),  # Tuples are not indexable
        ({}, "a", "x", "x"),  # Empty data
    ],
)
def test_deep_get(data: dict[str, Any], path: str, default: Any, expected: Any) -> None:
    """Should return the value at the path, or the default when it does not resolve."""
    assert deep_get(data, path, default) == expected


def test_deep_get_invalid_path() -> None:
    """Should raise a ValueError for a malformed path."""
    with pytest.raises(ValueError, match=re.escape("Invalid path: 'a..b'")):
        deep_get({"a": 1}, "a..b")


@suppress_type_checks
def test_deep_get_invalid_type() -> None:
    """Should raise a TypeError for invalid input."""
    with pytest.raises(TypeError, match=r"Input must be a dictionary."):
        deep_get([1, 2], "a")  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match=r"Path must be a string."):
        deep_get({"a": 1}, 1)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("data", "path", "value", "expected"),
    [
        ({}, "a", 1, {"a": 1}),  # Top-level key
        ({"a": 1}, "a", 2, {"a": 2}),  # Overwrite top-level key
        ({"a": 1}, "b", 2, {"a": 1, "b": 2}),  # Add sibling key
        ({}, "a.b.c", 1, {"a": {"b": {"c": 1}}}),  # Create intermediate dicts
        ({"a": {"b": 1}}, "a.c", 2, {"a": {"b": 1, "c": 2}}),  # Extend nested dict
        ({"a": {"b": 1}}, "a.b", 2, {"a": {"b": 2}}),  # Overwrite nested key
        ({"a": 1}, "a.b", 2, {"a": {"b": 2}}),  # Non-dict intermediate replaced
        ({"a": [10, 20]}, "a[1]", 99, {"a": [10, 99]}),  # Replace list element
        ({"a": [10, 20]}, "a[-1]", 99, {"a": [10, 99]}),  # Negative index
        ({"a": [{"b": 1}]}, "a[0].b", 2, {"a": [{"b": 2}]}),  # Set inside list element
        ({"a": [[1, 2]]}, "a[0][1]", 9, {"a": [[1, 9]]}),  # Chained indices
        ({}, "a[0].b", 1, {"a": {0: {"b": 1}}}),  # Missing list -> integer dict key, like pick
        ({"a": (1, 2)}, "a[0]", 9, {"a": {0: 9}}),  # Tuples are not indexable, replaced
        ({"a": {0: 1}}, "a[0]", 9, {"a": {0: 9}}),  # Bracket index overwrites an integer dict key
    ],
)
def test_deep_set(data: dict[str, Any], path: str, value: Any, expected: dict[str, Any]) -> None:
    """Should return a new dictionary with the value set at the path."""
    assert deep_set(data, path, value) == expected


def test_deep_set_does_not_mutate_input() -> None:
    """Should not mutate the input dictionary or the lists along the path."""
    data = {"a": {"b": [1, 2]}, "c": 3}
    result = deep_set(data, "a.b[0]", 99)
    assert data == {"a": {"b": [1, 2]}, "c": 3}
    assert result == {"a": {"b": [99, 2]}, "c": 3}
    assert result["a"] is not data["a"]
    assert result["a"]["b"] is not data["a"]["b"]


def test_deep_set_index_out_of_range() -> None:
    """Should raise an IndexError for an out-of-range index on an existing list."""
    with pytest.raises(IndexError, match=r"Index 5 out of range for list of length 2."):
        deep_set({"a": [1, 2]}, "a[5]", 3)


def test_deep_set_invalid_path() -> None:
    """Should raise a ValueError for a malformed path."""
    with pytest.raises(ValueError, match=re.escape("Invalid path: 'a['")):
        deep_set({"a": 1}, "a[", 2)


@suppress_type_checks
def test_deep_set_invalid_type() -> None:
    """Should raise a TypeError for invalid input."""
    with pytest.raises(TypeError, match=r"Input must be a dictionary."):
        deep_set([1, 2], "a", 1)  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match=r"Path must be a string."):
        deep_set({"a": 1}, 1, 1)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("data", "paths", "expected"),
    [
        ({"a": 1, "b": 2}, ("a",), {"b": 2}),  # Top-level key
        ({"a": 1, "b": 2, "c": 3}, ("a", "c"), {"b": 2}),  # Multiple paths
        ({"a": {"b": 1, "c": 2}}, ("a.b",), {"a": {"c": 2}}),  # Nested dict path
        ({"a": {"b": {"c": 1, "d": 2}}}, ("a.b.c",), {"a": {"b": {"d": 2}}}),  # Deeply nested
        ({"a": [10, 20, 30]}, ("a[1]",), {"a": [10, 30]}),  # List element removed, indices shift
        ({"a": [10, 20, 30]}, ("a[-1]",), {"a": [10, 20]}),  # Negative index
        ({"a": [{"b": 1, "c": 2}]}, ("a[0].b",), {"a": [{"c": 2}]}),  # Key inside list element
        ({"a": [[1, 2], [3]]}, ("a[0][1]",), {"a": [[1], [3]]}),  # Chained indices
        ({"a": [10, 20, 30]}, ("a[0]", "a[1]"), {"a": [20]}),  # Paths applied in order
        ({"a": {"0": 1}, "b": 2}, ("a.0",), {"a": {}, "b": 2}),  # Bare numeric segment is a dict key
        ({"a": {0: 1, 1: 2}}, ("a[0]",), {"a": {1: 2}}),  # Bracket index removes an integer dict key
        ({"a": {"b": 1}}, ("a.x",), {"a": {"b": 1}}),  # Missing key ignored
        ({"a": {"b": 1}}, ("x.y",), {"a": {"b": 1}}),  # Missing top-level key ignored
        ({"a": [1]}, ("a[5]",), {"a": [1]}),  # Index out of range ignored
        ({"a": 1}, ("a.b",), {"a": 1}),  # Non-dict intermediate ignored
        ({"a": {"b": 1}}, ("a[0]",), {"a": {"b": 1}}),  # Index into non-list ignored
        ({"a": (1, 2)}, ("a[0]",), {"a": (1, 2)}),  # Tuples are not indexable
        ({"a": 1}, (), {"a": 1}),  # No paths
        ({}, ("a",), {}),  # Empty data
    ],
)
def test_omit(data: dict[str, Any], paths: tuple[str, ...], expected: dict[str, Any]) -> None:
    """Should return a new dictionary without the omitted paths."""
    assert omit(data, *paths) == expected


def test_omit_does_not_mutate_input() -> None:
    """Should not mutate the input dictionary or the containers along omitted paths."""
    data = {"a": {"b": 1, "c": 2}, "d": [1, 2]}
    result = omit(data, "a.b", "d[0]")
    assert data == {"a": {"b": 1, "c": 2}, "d": [1, 2]}
    assert result == {"a": {"c": 2}, "d": [2]}
    assert result["a"] is not data["a"]
    assert result["d"] is not data["d"]


def test_omit_invalid_path() -> None:
    """Should raise a ValueError for a malformed path."""
    with pytest.raises(ValueError, match=re.escape("Invalid path: 'a..b'")):
        omit({"a": 1}, "a..b")


@suppress_type_checks
def test_omit_invalid_type() -> None:
    """Should raise a TypeError for invalid input."""
    with pytest.raises(TypeError, match=r"Input must be a dictionary."):
        omit([1, 2], "a")  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match=r"All paths must be strings."):
        omit({"a": 1}, 1)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("data", "paths", "expected"),
    [
        ({"a": 1, "b": 2}, ("a",), {"a": 1}),  # Top-level key
        ({"a": 1, "b": 2}, ("a", "b"), {"a": 1, "b": 2}),  # Multiple paths
        ({"a": {"b": {"c": 1}, "d": 2}}, ("a.b.c",), {"a": {"b": {"c": 1}}}),  # Nested dict path
        ({"a": [{"b": 1}, {"b": 2}]}, ("a[1].b",), {"a": {1: {"b": 2}}}),  # List index
        ({"a": [10, 20, 30]}, ("a[-1]",), {"a": {-1: 30}}),  # Negative index
        ({"a": [[1, 2], [3]]}, ("a[0][1]",), {"a": {0: {1: 2}}}),  # Chained indices
        ({"a": {"0": 1}, "b": [9]}, ("a.0",), {"a": {"0": 1}}),  # Bare numeric segment is a dict key
        ({"a": {0: 1}}, ("a[0]",), {"a": {0: 1}}),  # Bracket index resolves an integer dict key
        ({"a": {"b": 1}}, ("a.x",), {}),  # Missing key skipped
        ({"a": {"b": 1}}, ("x.y",), {}),  # Missing top-level key skipped
        ({"a": [1]}, ("a[5]",), {}),  # Index out of range skipped
        ({"a": 1}, ("a.b",), {}),  # Non-dict intermediate skipped
        ({"a": {"b": 1}}, ("a[0]",), {}),  # Index into non-list skipped
        ({"a": (1, 2)}, ("a[0]",), {}),  # Tuples are not indexable
        ({"a": {"b": 1, "c": 2}}, ("a", "a.b"), {"a": {"b": 1, "c": 2}}),  # Overlapping paths merge
        ({"a": {"b": 1}}, ("a.b", "a.b"), {"a": {"b": 1}}),  # Duplicate paths
        ({"a": 1}, (), {}),  # No paths
        ({}, ("a",), {}),  # Empty data
    ],
)
def test_pick(data: dict[str, Any], paths: tuple[str, ...], expected: dict[str, Any]) -> None:
    """Should return a new dictionary containing only the picked paths."""
    assert pick(data, *paths) == expected


def test_pick_round_trip() -> None:
    """Paths picked into integer dict keys should resolve with deep_get and omit again."""
    picked = pick({"a": [{"b": 1}, {"b": 2}]}, "a[1].b")
    assert picked == {"a": {1: {"b": 2}}}
    assert deep_get(picked, "a[1].b") == 2
    assert omit(picked, "a[1].b") == {"a": {1: {}}}


def test_pick_does_not_mutate_input() -> None:
    """Should not mutate the input dictionary when paths overlap."""
    data = {"a": {"b": 1, "c": 2}}
    result = pick(data, "a", "a.b")
    assert data == {"a": {"b": 1, "c": 2}}
    assert result["a"] is not data["a"]


@pytest.mark.parametrize("path", ["", ".", "a..b", ".a", "a.", "a[", "a[]", "a[1", "a[x]", "[0]", "a[0]b"])
def test_pick_invalid_path(path: str) -> None:
    """Should raise a ValueError for a malformed path."""
    with pytest.raises(ValueError, match=re.escape(f"Invalid path: {path!r}")):
        pick({"a": 1}, path)


@suppress_type_checks
def test_pick_invalid_type() -> None:
    """Should raise a TypeError for invalid input."""
    with pytest.raises(TypeError, match=r"Input must be a dictionary."):
        pick([1, 2], "a")  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError, match=r"All paths must be strings."):
        pick({"a": 1}, 1)  # ty: ignore[invalid-argument-type]

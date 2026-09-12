"""Tests for container utilities."""

import re
from collections.abc import Iterable
from operator import itemgetter
from typing import Any

import pytest
from typeguard import suppress_type_checks

from orval import chunkify, compact, deep_get, deep_merge, deep_set, flatten, is_empty, omit, pick, unique


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
    ("sequence", "expected"),
    [
        ([0, 1, None, 2, False, 3, ""], [0, 1, 2, False, 3, ""]),  # Keep falsy, drop None
        ([1, 2, 3], [1, 2, 3]),  # Nothing to remove
        ([None, None], []),  # Only None values
        ([0, "", False], [0, "", False]),  # Falsy but not None
        ([], []),  # Empty list
        ((0, "a", None), [0, "a"]),  # Tuple
        (range(3), [0, 1, 2]),  # Range
    ],
)
def test_compact(sequence: Iterable[Any], expected: list[Any]) -> None:
    """Should remove only None values by default."""
    assert compact(sequence) == expected


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ([0, 1, None, 2, False, 3, ""], [1, 2, 3]),  # Mixed falsy values
        ([None, False, 0, "", [], {}, ()], []),  # Only falsy values
        ([], []),  # Empty list
        (range(3), [1, 2]),  # Range
        ([[1], [], [2]], [[1], [2]]),  # Nested empty containers
    ],
)
def test_compact_falsy(sequence: Iterable[Any], expected: list[Any]) -> None:
    """Should remove all falsy values with none_only=False."""
    assert compact(sequence, none_only=False) == expected


def test_compact_varargs() -> None:
    """Should accept multiple values instead of a single iterable."""
    assert compact(0, 1, None, 2) == [0, 1, 2]
    assert compact(0, 1, None, 2, none_only=False) == [1, 2]
    assert compact(None) == []
    assert compact() == []
    assert compact("abc") == ["abc"]  # A single string is one value, not iterated.
    assert compact("a", None, "b") == ["a", "b"]


@pytest.mark.parametrize(
    ("sequence", "expected"),
    [
        ([3, 1, 3, 2, 1], [3, 1, 2]),  # Keeps the first occurrence, in order
        ([1, 2, 3], [1, 2, 3]),  # Nothing to remove
        ([], []),  # Empty list
        ([1, 1, 1], [1]),  # All duplicates
        ((1, 2, 1), [1, 2]),  # Tuple
        (range(3), [0, 1, 2]),  # Range
        ("banana", ["b", "a", "n"]),  # A string is iterated as characters
        ([None, None, 0, ""], [None, 0, ""]),  # Falsy values are kept, not dropped
        ([1, 1.0, True], [1]),  # Equal values collapse, as in a set: 1 == 1.0 == True
        ([0, False], [0]),  # Equal values collapse, as in a set: 0 == False
        ([{"a": 1}, {"a": 1}, {"b": 2}], [{"a": 1}, {"b": 2}]),  # Unhashable items
        ([[1], [1], [2]], [[1], [2]]),  # Unhashable items, mixed lengths
        ([{"a": 1}, 1, {"a": 1}, 1], [{"a": 1}, 1]),  # Hashable and unhashable mixed
    ],
)
def test_unique(sequence: Iterable[Any], expected: list[Any]) -> None:
    """Should drop duplicates while preserving the order of first appearance."""
    assert unique(sequence) == expected


def test_unique_generator() -> None:
    """Should consume an iterator exactly once."""
    assert unique(i % 3 for i in range(10)) == [0, 1, 2]


def test_unique_key() -> None:
    """Should deduplicate on the value returned by the key function."""
    assert unique(["Great", "great", "Scott"], key=str.lower) == ["Great", "Scott"]
    assert unique([1, -1, 2, -2, 3], key=abs) == [1, 2, 3]
    assert unique([{"id": 1}, {"id": 1}, {"id": 2}], key=itemgetter("id")) == [{"id": 1}, {"id": 2}]


def test_unique_tuple_key() -> None:
    """Should deduplicate on a combination of fields when the key returns a tuple."""
    rows = [
        {"first": "Marty", "last": "McFly"},
        {"first": "Marty", "last": "Brown"},
        {"first": "Marty", "last": "McFly"},
    ]
    assert unique(rows, key=itemgetter("first", "last")) == rows[:2]


def test_unique_unhashable_key() -> None:
    """Should deduplicate on key values that cannot be hashed."""
    rows = [{"tags": ["a"]}, {"tags": ["a"]}, {"tags": ["b"]}]
    assert unique(rows, key=itemgetter("tags")) == [{"tags": ["a"]}, {"tags": ["b"]}]


def test_unique_multiple_keys() -> None:
    """Should drop an item that collides on any one of the key functions."""
    rows = [
        {"id": 1, "email": "marty@bttf.com"},  # Kept, so its id and email are remembered
        {"id": 2, "email": "marty@bttf.com"},  # Dropped: the email of a kept item
        {"id": 1, "email": "doc@bttf.com"},  # Dropped: the id of a kept item
        {"id": 3, "email": "doc@bttf.com"},  # Kept: no kept item had id 3 or that email
        {"id": 4, "email": "jennifer@bttf.com"},  # Kept: neither key collides
    ]
    keys = [itemgetter("id"), itemgetter("email")]
    assert unique(rows, key=keys) == [rows[0], rows[3], rows[4]]


def test_unique_keys_do_not_collide() -> None:
    """Should keep the values of different key functions apart."""
    rows = [{"a": 1, "b": 2}, {"a": 2, "b": 1}]
    assert unique(rows, key=[itemgetter("a"), itemgetter("b")]) == rows


def test_unique_only_kept_items_are_remembered() -> None:
    """Should compare later items against the kept ones, not against the dropped ones."""
    rows = [
        {"id": 1, "email": "marty@bttf.com"},
        {"id": 2, "email": "marty@bttf.com"},  # Dropped: its id 2 is not remembered
        {"id": 2, "email": "doc@bttf.com"},  # Kept: id 2 was never kept before
    ]
    assert unique(rows, key=[itemgetter("id"), itemgetter("email")]) == [rows[0], rows[2]]


def test_unique_key_called_once_per_item() -> None:
    """Should stop at the first colliding key function instead of calling them all."""
    calls: list[str] = []

    def first(item: dict[str, int]) -> int:
        calls.append("first")
        return item["a"]

    def second(item: dict[str, int]) -> int:
        calls.append("second")
        return item["b"]

    assert unique([{"a": 1, "b": 1}, {"a": 1, "b": 2}], key=[first, second]) == [{"a": 1, "b": 1}]
    assert calls == ["first", "second", "first"]


def test_unique_empty_keys() -> None:
    """Should raise a ValueError for an empty iterable of key functions."""
    with pytest.raises(ValueError, match=re.escape("Key must contain at least one callable.")):
        unique([1, 2], key=[])


@suppress_type_checks
def test_unique_invalid_key() -> None:
    """Should raise a TypeError for a key that is not a callable or an iterable of callables."""
    with pytest.raises(TypeError, match=re.escape("Key must be a callable or an iterable of callables.")):
        unique([1, 2], key=["not a callable"])  # ty: ignore[invalid-argument-type]
    with pytest.raises(TypeError):
        unique([1, 2], key=42)  # ty: ignore[invalid-argument-type]


def test_unique_does_not_mutate_input() -> None:
    """Should leave the input sequence untouched."""
    sequence = [1, 2, 1]
    assert unique(sequence) == [1, 2]
    assert sequence == [1, 2, 1]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, True),  # None is empty
        ("", True),  # Empty string
        (b"", True),  # Empty bytes
        ([], True),  # Empty list
        ((), True),  # Empty tuple
        ({}, True),  # Empty dict
        (set(), True),  # Empty set
        (frozenset(), True),  # Empty frozenset
        (range(0), True),  # Empty range
        ("  ", False),  # Whitespace-only string is not empty
        ("a", False),  # Non-empty string
        (b"x", False),  # Non-empty bytes
        ([0], False),  # Non-empty list, even with a falsy element
        ({"a": 1}, False),  # Non-empty dict
        ({0}, False),  # Non-empty set
        (range(3), False),  # Non-empty range
        (0, False),  # Zero is not empty
        (0.0, False),  # Zero float is not empty
        (False, False),  # False is not empty
        (True, False),  # True is not empty
        (object(), False),  # Arbitrary object is not empty
        ((i for i in []), False),  # Generators have no length, never empty
    ],
)
def test_is_empty(value: Any, expected: bool) -> None:
    """Should report None and sized containers without elements as empty."""
    assert is_empty(value) is expected


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


def test_omit_shares_untouched_subtrees() -> None:
    """Should not copy containers when the path does not resolve."""
    data = {"a": {"b": 1}, "c": [1, 2]}
    result = omit(data, "a.x", "a.b.c", "c[5]")
    assert result == data
    assert result["a"] is data["a"]
    assert result["c"] is data["c"]


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

"""Array utilities."""

import re
from collections.abc import Callable, Generator, Iterable, Sized
from itertools import islice
from typing import Any, TypeVar, cast

T = TypeVar("T")
_PATH_RE = re.compile(r"[^.\[\]]+(?:\[-?\d+\])*(?:\.[^.\[\]]+(?:\[-?\d+\])*)*")
_TOKEN_RE = re.compile(r"([^.\[\]]+)|\[(-?\d+)\]")
_MISSING = object()


def chunkify(seq: Iterable[T], s: int) -> list[list[T]]:  # ruff: ignore[non-pep695-generic-function]
    """Break an interable into chunks of size S.

    Parameters
    ----------
    seq : Iterable
        The iterable to chunk.
    s : int
        The size of each chunk.

    Returns
    -------
    list
        A list of chunks.
    """
    if s < 1:
        raise ValueError(f"Size must be > 0, invalid value {s}")

    def _inner(_seq: Iterable[T], _s: int) -> Generator[list[T]]:
        iterator = iter(_seq)
        while True:
            chunk = list(islice(iterator, _s))
            if not chunk:
                break
            yield chunk

    return list(_inner(seq, s))


def flatten(seq: Iterable[T], depth: int | None = None) -> Generator[T]:  # ruff: ignore[non-pep695-generic-function]
    """Flattens a nested iterable up to a specified depth.

    Parameters
    ----------
    seq : Iterable
        The iterable or set to flatten.
    depth : int, optional
        The depth to flatten to. If None, flattens completely.

    Returns
    -------
    Generator
        The flattened sequence.
    """
    # Caveat: the error is only raised when the generator is consumed
    if depth is not None and depth < 0:
        raise ValueError(f"Depth must be >= 0, invalid value {depth}")
    if not isinstance(seq, Iterable):
        raise TypeError("Input must be an interable (list, set, range, tuple).")
    if isinstance(seq, str):
        yield seq  # ty: ignore[invalid-yield]
        return

    def _flatten(_seq: Iterable[T], current_depth: int) -> Generator[T]:
        if depth is not None and current_depth >= depth:
            yield from _seq
            return
        for item in _seq:
            if isinstance(item, Iterable) and not isinstance(item, str):
                yield from _flatten(item, current_depth + 1)  # type: ignore[invalid-argument-type]
            else:
                yield item

    yield from _flatten(seq, 0)


def compact(*seq: T | Iterable[T], none_only: bool = True) -> list[T]:  # ruff: ignore[non-pep695-generic-function]
    """Remove None or falsy values from an iterable or from the given arguments.

    Accepts either a single iterable (``compact([0, 1, None])``) or multiple values
    (``compact(0, 1, None)``). By default only ``None`` values are removed, keeping
    legitimate falsy values such as ``0`` or ``""``. With ``none_only=False`` all falsy
    values are removed: ``None``, ``False``, ``0``, ``""``, empty collections, etc.
    A single string or bytes argument is treated as one value, not iterated.

    Parameters
    ----------
    *seq
        A single iterable to compact, or multiple values to compact.
    none_only : bool, optional
        If True (the default), only remove ``None`` values instead of all falsy values.

    Returns
    -------
    list
        A new list without the removed values.

    Examples
    --------
    >>> compact([0, 1, None, 2, False, 3, ""])
    [0, 1, 2, False, 3, '']
    >>> compact(0, 1, None, 2)
    [0, 1, 2]
    >>> compact([0, 1, None, 2, False, 3, ""], none_only=False)
    [1, 2, 3]
    """
    items: Iterable[T] = cast("Iterable[T]", seq)
    if len(seq) == 1 and isinstance(seq[0], Iterable) and not isinstance(seq[0], str | bytes):
        items = cast("Iterable[T]", seq[0])
    if none_only:
        return [item for item in items if item is not None]
    return [item for item in items if item]


class _Unhashable:
    """An unhashable key value wrapped so it can live in a set, comparing by equality."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value

    def __hash__(self) -> int:
        # A constant hash puts every unhashable value in one bucket, where __eq__ decides.
        return 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Unhashable):
            return False
        if self.value is other.value:
            return True
        try:
            return bool(self.value == other.value)
        except (TypeError, ValueError):
            # An equality that is not a boolean (a numpy array, a pandas Series) decides nothing.
            return False


def _mark(value: Any) -> Any:
    """Return a hashable stand-in for a key value, wrapping it when it cannot be hashed."""
    try:
        hash(value)
    except TypeError:
        return _Unhashable(value)
    return value


def unique(seq: Iterable[T], key: Callable[[T], Any] | Iterable[Callable[[T], Any]] | None = None) -> list[T]:  # ruff: ignore[non-pep695-generic-function]
    """Remove duplicates from an iterable, keeping the first occurrence of each item.

    The order of the remaining items is preserved, unlike ``set(seq)``. Items are compared by
    equality and do not have to be hashable: dictionaries, lists and other unhashable values
    work too, at the cost of a linear scan over the unhashable values seen so far. Values whose
    ``==`` answers with something other than a boolean, such as a numpy array or a pandas
    Series, are kept as distinct unless they are the same object, rather than raising.

    ``key`` decides what makes two items duplicates. A single callable deduplicates on its
    return value, so a callable returning a tuple deduplicates on a combination of fields. An
    iterable of callables deduplicates on *any* of them: an item is dropped as soon as one of
    the key functions returns a value that function returned for an earlier item, which is what
    you want when several fields each identify an item on their own. The key functions do not
    collide with each other; each one remembers its own values. Only kept items are remembered,
    so the first item of a group decides what the ones after it collide with.

    Parameters
    ----------
    seq : Iterable
        The iterable to deduplicate.
    key : Callable or Iterable of Callable, optional
        A function of one item returning the value to deduplicate on, or an iterable of such
        functions to deduplicate on any of them. Defaults to the items themselves.

    Returns
    -------
    list
        A new list without duplicates, in order of first appearance.

    Raises
    ------
    TypeError
        If key is neither a callable nor an iterable of callables.
    ValueError
        If key is an empty iterable.

    Examples
    --------
    >>> unique([3, 1, 3, 2, 1])
    [3, 1, 2]
    >>> unique(["Great", "great", "Scott"], key=str.lower)
    ['Great', 'Scott']
    >>> unique([{"a": 1}, {"a": 1}, {"b": 2}])
    [{'a': 1}, {'b': 2}]
    >>> rows = [{"id": 1, "email": "marty@bttf.com"}, {"id": 2, "email": "marty@bttf.com"}]
    >>> unique(rows, key=[lambda r: r["id"], lambda r: r["email"]])
    [{'id': 1, 'email': 'marty@bttf.com'}]
    """
    if key is None:
        funcs: tuple[Callable[[T], Any], ...] = (lambda item: item,)
    elif callable(key):
        # A key that is both callable and iterable is treated as one key function.
        funcs = (cast("Callable[[T], Any]", key),)
    else:
        if not isinstance(key, Iterable):
            raise TypeError("Key must be a callable or an iterable of callables.")
        funcs = tuple(key)
        if not funcs:
            raise ValueError("Key must contain at least one callable.")
        if not all(callable(func) for func in funcs):
            raise TypeError("Key must be a callable or an iterable of callables.")
    seen: list[set[Any]] = [set() for _ in funcs]
    result: list[T] = []
    for item in seq:
        marks: list[tuple[Any, set[Any]]] = []
        for func, values in zip(funcs, seen, strict=True):
            mark = _mark(func(item))
            if mark in values:
                break
            marks.append((mark, values))
        else:
            result.append(item)
            for mark, values in marks:
                values.add(mark)
    return result


def is_empty(value: Any) -> bool:
    """Check whether a value is empty.

    A value is empty when it is ``None`` or a sized container without elements: ``""``,
    ``b""``, ``[]``, ``()``, ``{}``, ``set()``, ``range(0)``, etc. Emptiness is not
    truthiness: values without a length — numbers, booleans, generators, arbitrary
    objects — are never empty, so ``0`` and ``False`` are kept apart from ``None`` and
    ``[]``. A whitespace-only string is not empty; strip it first if needed.

    Parameters
    ----------
    value
        The value to check.

    Returns
    -------
    bool
        True when the value is None or a sized container without elements.

    Examples
    --------
    >>> is_empty(None)
    True
    >>> is_empty([])
    True
    >>> is_empty("")
    True
    >>> is_empty(0)
    False
    >>> is_empty(False)
    False
    """
    return value is None or (isinstance(value, Sized) and len(value) == 0)


def deep_merge(*dicts: dict[Any, Any]) -> dict[Any, Any]:
    """Deep merge multiple dictionaries.

    Parameters
    ----------
      *dicts: One or more dictionaries to merge.

    Returns
    -------
    dict
        The merged dictionary.
    """
    if not all(isinstance(d, dict) for d in dicts):
        raise TypeError("All inputs must be dictionaries.")
    result: dict[Any, Any] = {}
    for d in dicts:
        for k, v in d.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = deep_merge(result[k], v)
            else:
                result[k] = v
    return result


def _parse_path(path: str) -> list[str | int]:
    """Parse a path like "a.b[0].c" into a list of dict keys (str) and list indices (int)."""
    if not _PATH_RE.fullmatch(path):
        raise ValueError(f"Invalid path: {path!r}")
    return [match[1] if match[1] is not None else int(match[2]) for match in _TOKEN_RE.finditer(path)]


def _resolve(data: dict[Any, Any], keys: list[str | int]) -> Any:
    """Walk the keys through nested dicts/lists, returning the value or the _MISSING sentinel.

    A bracket index (int key) resolves a list position, or an integer dictionary key when the
    container is a dictionary, as produced by pick and deep_set.
    """
    current: Any = data
    for key in keys:
        if isinstance(current, list) and isinstance(key, int):
            if not -len(current) <= key < len(current):
                return _MISSING
        elif not isinstance(current, dict) or key not in current:
            return _MISSING
        current = current[key]
    return current


def deep_get(data: dict[str, Any], /, path: str, default: Any = None) -> Any:
    """Get a value from a nested dictionary by path, returning a default if the path does not resolve.

    Paths use dot notation for dictionary keys and brackets for list indices, e.g. "a.b[0].c".
    Bracket indices may be negative. A bracket index resolves a list position, or an integer
    dictionary key when the container is a dictionary, as produced by pick and deep_set.

    Parameters
    ----------
    data
        The dictionary to read from.
    path
        The path to resolve, e.g. "a.b[0].c".
    default
        The value returned when the path does not resolve. Defaults to None.

    Returns
    -------
    Any
        The value at the path, or the default.

    Raises
    ------
    TypeError
        If the input is not a dictionary or the path is not a string.
    ValueError
        If the path is malformed.
    """
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary.")
    if not isinstance(path, str):
        raise TypeError("Path must be a string.")
    value = _resolve(data, _parse_path(path))
    return default if value is _MISSING else value


def _assign(current: Any, keys: list[str | int], value: Any) -> Any:
    """Return current with the value set at the keys, copying containers along the path."""
    if not keys:
        return value
    key, rest = keys[0], keys[1:]
    if isinstance(key, int) and isinstance(current, list):
        if not -len(current) <= key < len(current):
            raise IndexError(f"Index {key} out of range for list of length {len(current)}.")
        items: Any = list(current)
    else:
        items = dict(current) if isinstance(current, dict) else {}
    items[key] = _assign(items.get(key) if isinstance(items, dict) else items[key], rest, value)
    return items


def deep_set(data: dict[str, Any], /, path: str, value: Any) -> dict[str, Any]:
    """Set a value in a nested dictionary by path, creating intermediate dictionaries as needed.

    Paths use dot notation for dictionary keys and brackets for list indices, e.g. "a.b[0].c".
    A bracket index into an existing list replaces that element (negative indices allowed);
    anywhere else the index becomes an integer dictionary key, mirroring pick. Intermediate
    values that cannot hold the next segment are replaced by new dictionaries. The input is not
    mutated: containers along the path are copied, but untouched subtrees are shared with the
    input, not copied.

    Parameters
    ----------
    data
        The dictionary to set the value in.
    path
        The path to set, e.g. "a.b[0].c".
    value
        The value to set at the path.

    Returns
    -------
    dict
        A new dictionary with the value set at the path.

    Raises
    ------
    TypeError
        If the input is not a dictionary or the path is not a string.
    ValueError
        If the path is malformed.
    IndexError
        If a bracket index is out of range for an existing list.
    """
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary.")
    if not isinstance(path, str):
        raise TypeError("Path must be a string.")
    result: dict[str, Any] = _assign(data, _parse_path(path), value)
    return result


def _drop(current: Any, keys: list[str | int]) -> Any:
    """Return current with the path removed, copying containers along the path.

    Returns the input unchanged when the path does not resolve.
    """
    key: Any = keys[0]
    rest = keys[1:]
    if isinstance(current, list) and isinstance(key, int):
        if not -len(current) <= key < len(current):
            return current
    elif not isinstance(current, dict) or key not in current:
        return current
    if rest:
        child = _drop(current[key], rest)
        if child is current[key]:
            return current
        items: Any = list(current) if isinstance(current, list) else dict(current)
        items[key] = child
        return items
    items = list(current) if isinstance(current, list) else dict(current)
    del items[key]
    return items


def omit(data: dict[str, Any], /, *paths: str) -> dict[str, Any]:
    """Omit paths from a nested dictionary, keeping everything else.

    The opposite of pick. Paths use dot notation for dictionary keys and brackets for list
    indices, e.g. "a.b[0].c". Bracket indices may be negative and remove the element from the
    list, shifting later elements; on a dictionary, as produced by pick and deep_set, a bracket
    index removes the integer key instead. Paths that do not resolve are silently ignored, and
    paths are applied in order, each against the result of the previous one. The input is not mutated:
    containers along omitted paths are copied, but untouched subtrees are shared with the input,
    not copied.

    Parameters
    ----------
    data
        The dictionary to omit from.
    *paths
        One or more paths to omit, e.g. "a.b[0].c".

    Returns
    -------
    dict
        A new dictionary without the omitted paths.

    Raises
    ------
    TypeError
        If the input is not a dictionary or a path is not a string.
    ValueError
        If a path is malformed.
    """
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary.")
    if not all(isinstance(p, str) for p in paths):
        raise TypeError("All paths must be strings.")
    result: dict[str, Any] = dict(data)
    for path in paths:
        result = _drop(result, _parse_path(path))
    return result


def pick(data: dict[str, Any], /, *paths: str) -> dict[str, Any]:
    """Pick values from a nested dictionary, preserving the nested structure.

    Paths use dot notation for dictionary keys and brackets for list indices, e.g. "a.b[0].c".
    Bracket indices may be negative and appear as integer keys in the result; they also resolve
    integer dictionary keys when the container is a dictionary. Paths that do not
    resolve are silently skipped. The result is a newly built structure and overlapping paths are
    deep-merged into new dictionaries, but the picked leaf values themselves are not copied.

    Parameters
    ----------
    data
        The dictionary to pick from.
    *paths
        One or more paths to pick, e.g. "a.b[0].c".

    Returns
    -------
    dict
        A new nested dictionary containing only the picked paths.

    Raises
    ------
    TypeError
        If the input is not a dictionary or a path is not a string.
    ValueError
        If a path is malformed.
    """
    if not isinstance(data, dict):
        raise TypeError("Input must be a dictionary.")
    if not all(isinstance(p, str) for p in paths):
        raise TypeError("All paths must be strings.")
    result: dict[str, Any] = {}
    for path in paths:
        keys = _parse_path(path)
        value = _resolve(data, keys)
        if value is _MISSING:
            continue
        contribution: Any = value
        for key in reversed(keys):
            contribution = {key: contribution}
        result = deep_merge(result, contribution)
    return result

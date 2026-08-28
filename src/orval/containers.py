"""Array utilities."""

import re
from collections.abc import Generator, Iterable
from itertools import islice
from typing import Any, TypeVar

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

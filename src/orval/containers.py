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


def compact(seq: Iterable[T], *, none_only: bool = False) -> list[T]:  # ruff: ignore[non-pep695-generic-function]
    """Remove falsy values from an iterable.

    By default all falsy values are removed: ``None``, ``False``, ``0``, ``""``, empty
    collections, etc. With ``none_only=True`` only ``None`` values are removed, keeping
    legitimate falsy values such as ``0`` or ``""``.

    Parameters
    ----------
    seq : Iterable
        The iterable to compact.
    none_only : bool, optional
        If True, only remove ``None`` values instead of all falsy values.

    Returns
    -------
    list
        A new list without the removed values.

    Examples
    --------
    >>> compact([0, 1, None, 2, False, 3, ""])
    [1, 2, 3]
    >>> compact([0, 1, None, 2, False, 3, ""], none_only=True)
    [0, 1, 2, False, 3, '']
    """
    if not isinstance(seq, Iterable) or isinstance(seq, str):
        raise TypeError("Input must be an iterable (list, set, range, tuple).")
    if none_only:
        return [item for item in seq if item is not None]
    return [item for item in seq if item]


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
    """Walk the keys through nested dicts/lists, returning the value or the _MISSING sentinel."""
    current: Any = data
    for key in keys:
        if isinstance(key, str):
            if not isinstance(current, dict) or key not in current:
                return _MISSING
        elif not isinstance(current, list) or not -len(current) <= key < len(current):
            return _MISSING
        current = current[key]
    return current


def pick(data: dict[str, Any], /, *paths: str) -> dict[str, Any]:
    """Pick values from a nested dictionary, preserving the nested structure.

    Paths use dot notation for dictionary keys and brackets for list indices, e.g. "a.b[0].c".
    Bracket indices may be negative and appear as integer keys in the result. Paths that do not
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

"""Array utilities."""

from collections.abc import Generator, Iterable
from itertools import islice
from typing import Any, TypeVar

T = TypeVar("T")


def chunkify(seq: Iterable[T], s: int) -> list[list[T]]:
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


def flatten(seq: Iterable[T], depth: int | None = None) -> Generator[T]:
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
        yield seq
        return

    def _flatten(_seq: Iterable[T], current_depth: int) -> Generator[T]:
        if depth is not None and current_depth >= depth:
            yield from _seq
            return
        for item in _seq:
            if isinstance(item, Iterable) and not isinstance(item, str):
                yield from _flatten(item, current_depth + 1)
            else:
                yield item  # type: ignore[misc]

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

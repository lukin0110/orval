"""Array utilities."""

from collections.abc import Generator, Sequence
from typing import TypeVar

T = TypeVar("T")


def chunkify(seq: list[T], s: int) -> list[list[T]]:
    """Break a list into chunks of size S."""
    if s < 1:
        raise ValueError(f"Size must be > 0, invalid value {s}")
    return [seq[pos : pos + s] for pos in range(0, len(seq), s)]


def flatten(seq: Sequence[T] | set[T], depth: int | None = None) -> Generator[T]:
    """Flattens a nested sequence or set up to a specified depth.

    Parameters
    ----------
    seq : Sequence | set
        The sequence or set to flatten.
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
    if not isinstance(seq, Sequence | set):
        raise TypeError("Input must be a sequence or set.")
    if isinstance(seq, str):
        yield seq
        return

    def _flatten(_seq: Sequence[T] | set[T], current_depth: int) -> Generator[T]:
        if depth is not None and current_depth >= depth:
            yield from _seq
            return
        for item in _seq:
            if isinstance(item, Sequence | set) and not isinstance(item, str):
                yield from _flatten(item, current_depth + 1)
            else:
                yield item  # type: ignore[misc]

    yield from _flatten(seq, 0)

"""Array utilities."""

from typing import TypeVar

T = TypeVar("T")


def chunkify(seq: list[T], s: int) -> list[list[T]]:
    """Break a list into chunks of size S."""
    if s < 1:
        raise ValueError(f"Size must be > 0, invalid value {s}")
    return [seq[pos : pos + s] for pos in range(0, len(seq), s)]

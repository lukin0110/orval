"""Utilities."""

import logging
import time
from collections.abc import Callable
from functools import partial
from typing import Any, TypeVar

R = TypeVar("R")


def timing(func: Callable[..., R] | None = None, level: int = logging.INFO) -> Any:
    """Log the elapsed time of a function.

    Decorator can be used with or without arguments. Eg: `@timing` or `@timing(level=logging.DEBUG)`.

    Parameters
    ----------
    func
        The wrapped function to log the elapsed time of.
    level
        Log level to user. Default: INFO.

    Returns
    -------
    Any
        The function wrapped to log timing.
    """
    if func is None:
        return partial(timing, level=level)

    def wrapper(
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> Any:
        """Log elapsed time of the wrapped function."""
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.getLogger(__name__).log(level, f"Timing for '{func.__name__}': {end - start:.3f}s")
        return result

    return wrapper

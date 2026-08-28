"""Utilities."""

import logging
import time
from collections.abc import Callable
from functools import partial
from typing import Any, TypeVar

R = TypeVar("R")
T = TypeVar("T")


def coalesce(*values: T | None, default: T | None = None) -> T | None:  # ruff: ignore[non-pep695-generic-function]
    """Return the first value that is not None.

    Borrowed from SQL's COALESCE and equivalent to chaining the ``??`` operator in
    JavaScript. Unlike chaining ``or``, falsy values such as ``0``, ``""``, and ``False``
    are kept, since the test is "is not None" rather than truthiness. This makes it
    well-suited for config/fallback chains where e.g. ``port=0`` or ``debug=False``
    are valid values.

    Parameters
    ----------
    *values
        The values to consider, in order of preference.
    default
        Value returned when all values are None (default is None).

    Returns
    -------
    T | None
        The first value that is not None, or 'default' when all values are None.

    Examples
    --------
    >>> coalesce(None, None, 0, 5)
    0
    >>> coalesce(None, None, default=8080)
    8080
    """
    return next((value for value in values if value is not None), default)


def coalesce_lazy(*values: Callable[[], T | None], default: T | None = None) -> T | None:  # ruff: ignore[non-pep695-generic-function]
    """Return the first callable's result that is not None, calling them lazily.

    The lazy variant of `coalesce`: each argument is a zero-argument callable that is
    only invoked when all previous ones returned None. Use this when fallbacks are
    expensive to compute (e.g. a database lookup behind a cache lookup).

    Parameters
    ----------
    *values
        Zero-argument callables producing the values to consider, in order of preference.
    default
        Value returned when all callables return None (default is None).

    Returns
    -------
    T | None
        The first result that is not None, or 'default' when all results are None.

    Examples
    --------
    >>> coalesce_lazy(lambda: None, lambda: 0, lambda: 1 / 0)
    0
    >>> coalesce_lazy(lambda: None, default=8080)
    8080
    """
    return next((result for value in values if (result := value()) is not None), default)


def timing(func: Callable[..., R] | None = None, level: int = logging.INFO) -> Any:  # ruff: ignore[non-pep695-generic-function]
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
        logging.getLogger(__name__).log(level, f"Timing for '{func.__name__}': {end - start:.3f}s")  # ty: ignore[unresolved-attribute]
        return result

    return wrapper

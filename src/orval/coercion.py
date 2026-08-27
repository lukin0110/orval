"""Coercion utilities.

Lenient conversion of loosely-typed input (environment variables, query parameters,
config files, CSV cells) into booleans, integers, and floats.
"""

_TRUTHY = frozenset({"true", "t", "yes", "y", "on", "1"})
_FALSY = frozenset({"false", "f", "no", "n", "off", "0"})


def to_bool(value: object, default: bool | None = None) -> bool:
    """Convert a value to a boolean.

    Recognizes common textual representations, case-insensitively and ignoring
    surrounding whitespace:

    - Truthy: ``"true"``, ``"t"``, ``"yes"``, ``"y"``, ``"on"``, ``"1"``
    - Falsy: ``"false"``, ``"f"``, ``"no"``, ``"n"``, ``"off"``, ``"0"``

    Booleans are returned as-is and the numbers ``1``/``0`` map to ``True``/``False``.
    Any other value returns 'default' when given, otherwise a ValueError is raised.

    Parameters
    ----------
    value
        The value to convert.
    default
        Value returned when the input is not recognized. If None (the default),
        an unrecognized input raises a ValueError instead.

    Returns
    -------
    bool
        The converted boolean.

    Raises
    ------
    ValueError
        If the value is not recognized and no 'default' is given.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        if text in _TRUTHY:
            return True
        if text in _FALSY:
            return False
    if default is not None:
        return default
    raise ValueError(f"Cannot convert {value!r} to bool.")


def safe_int(value: object, default: int | None = None) -> int | None:
    """Convert a value to an integer, returning a default on failure.

    Strings are parsed leniently: surrounding whitespace is ignored and decimal
    notation is accepted by truncating towards zero (e.g. ``"3.7"`` becomes ``3``).

    Parameters
    ----------
    value
        The value to convert.
    default
        Value returned when the input cannot be converted (default is None).

    Returns
    -------
    int | None
        The converted integer, or 'default' when conversion fails.
    """
    try:
        return int(value)  # ty: ignore[invalid-argument-type]
    except (TypeError, ValueError):
        pass
    try:
        return int(float(value))  # ty: ignore[invalid-argument-type]
    except (TypeError, ValueError, OverflowError):
        return default


def safe_float(value: object, default: float | None = None) -> float | None:
    """Convert a value to a float, returning a default on failure.

    Surrounding whitespace in strings is ignored. Note that ``"inf"`` and ``"nan"``
    are valid floats and parse successfully.

    Parameters
    ----------
    value
        The value to convert.
    default
        Value returned when the input cannot be converted (default is None).

    Returns
    -------
    float | None
        The converted float, or 'default' when conversion fails.
    """
    try:
        return float(value)  # ty: ignore[invalid-argument-type]
    except (TypeError, ValueError):
        return default

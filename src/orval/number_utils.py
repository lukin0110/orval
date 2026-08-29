"""Utility functions for working with numbers."""

import math

_BASE: int = 1000

# short, long
_UNITS: list[tuple[str, str]] = [
    ("", ""),
    ("K", "thousand"),
    ("M", "million"),
    ("B", "billion"),
    ("T", "trillion"),
]

# short, long
_FORMATS: set[str] = {"s", "l"}


def _validate_arguments(value: float, fmt: str, precision: int) -> None:
    """Validate pretty_number arguments, raising TypeError or ValueError."""
    if not isinstance(value, int | float):
        raise TypeError("Value must be a number.")
    if fmt not in _FORMATS:
        raise ValueError(f"Format must be one of {_FORMATS}.\n  s: short (e.g. 1.2M)\n  l: long (e.g. 1.2 million)")
    if not isinstance(precision, int):
        raise TypeError("Precision must be an integer.")
    if precision < 0:
        raise ValueError("Precision must be a non-negative integer.")


def pretty_number(value: float, fmt: str = "s", /, precision: int = 1) -> str:
    """Convert a number to a compact human-readable string.

    The number is scaled to the largest short-scale unit below it (e.g., 1234567
    becomes "1.2M"). Trailing zeros are stripped, so 1000 becomes "1K" rather than
    "1.0K". Values above a trillion stay expressed in trillions. Negative numbers
    keep their sign.

    Available formats:
    - s: short (e.g., 1.2M)
    - l: long (e.g., 1.2 million)

    Parameters
    ----------
    value : float
        The number to format.
    fmt : str
        The format to use. One of "s", "l". Default is "s".
    precision : int
        The maximum number of decimal places to round to.

    Returns
    -------
    str
        The formatted number as a human-readable string.
    """
    _validate_arguments(value, fmt, precision)
    sign = "-" if value < 0 else ""
    try:
        scaled: float = float(abs(value))
    except OverflowError:
        # Integers beyond the float range (~1.8e308) cannot be scaled.
        raise ValueError("Value is too large to format.") from None
    if not math.isfinite(scaled):
        raise ValueError("Value must be finite.")
    index = 0
    while scaled >= _BASE and index < len(_UNITS) - 1:
        scaled /= _BASE
        index += 1
    # Rounding may carry into the next unit (e.g. 999950 -> 1000.0K -> 1M).
    if round(scaled, precision) >= _BASE and index < len(_UNITS) - 1:
        scaled /= _BASE
        index += 1
    number = f"{scaled:.{precision}f}"
    if "." in number:
        number = number.rstrip("0").rstrip(".")
    if number == "0":
        # A negative value that rounds to zero must not render as "-0".
        sign = ""
    unit = _UNITS[index][0] if fmt == "s" else _UNITS[index][1]
    separator = " " if fmt == "l" and unit else ""
    return f"{sign}{number}{separator}{unit}"

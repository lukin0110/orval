"""Utility functions for working with bytes."""

import math
import re

_BASE_1000: int = 1000
_BASE_1024: int = 1024

# Units decimal: base 1000
_UNITS_DECIMAL_SHORT: list[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
_UNITS_DECIMAL_LONG: list[str] = [
    "Bytes",
    "Kilobytes",
    "Megabytes",
    "Gigabytes",
    "Terabytes",
    "Petabytes",
    "Exabytes",
    "Zettabytes",
    "Yottabytes",
]

# Unit binary: base 1024
_UNITS_BINARY_SHORT: list[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
_UNITS_BINARY_LONG: list[str] = [
    "Bytes",
    "Kibibytes",
    "Mebibytes",
    "Gibibytes",
    "Tebibytes",
    "Pebibytes",
    "Exbibytes",
    "Zebibytes",
    "Yobibytes",
]

# decimal-short, decimal-long, binary-short, binary-long
_FORMATS: set[str] = {"ds", "dl", "bs", "bl"}

_PARSE_PATTERN: re.Pattern[str] = re.compile(r"^(?P<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(?P<unit>[A-Za-z]*)$")


def _build_unit_multipliers() -> dict[str, int]:
    multipliers: dict[str, int] = {}
    for units, base in (
        (_UNITS_DECIMAL_SHORT, _BASE_1000),
        (_UNITS_DECIMAL_LONG, _BASE_1000),
        (_UNITS_BINARY_SHORT, _BASE_1024),
        (_UNITS_BINARY_LONG, _BASE_1024),
    ):
        for exponent, unit in enumerate(units):
            multipliers[unit.lower()] = base**exponent
    return multipliers


_UNIT_MULTIPLIERS: dict[str, int] = _build_unit_multipliers()


def pretty_bytes(size: int, fmt: str = "ds", /, precision: int = 2) -> str:
    """Convert a size in bytes to a human-readable string.

    By default, a short decimal format with base 1.000 is used (e.g., 1.23 KB).

    Available formats:
    - ds: decimal-short (e.g., 1.23 KB)
    - dl: decimal-long (e.g., 1.23 Kilobytes)
    - bs: binary-short (e.g., 1.23 KiB)
    - bl: binary-long (e.g., 1.23 Kibibytes)

    Parameters
    ----------
    size : int
        The size in bytes.
    fmt : str
        The format to use. One of "ds", "dl", "bs", "bl". Default is "ds".
    precision : int
        The number of decimal places to round to.

    Returns
    -------
    str
        The formatted disk size as a human-readable string.
    """
    if not isinstance(size, int):
        raise TypeError("Size must be an integer.")
    if size < 0:
        raise ValueError("Size must be a non-negative integer.")
    if fmt not in _FORMATS:
        raise ValueError(
            f"Format must be one of {_FORMATS}.\n  ds: decimal short (e.g. MB)\n  dl: decimal long (e.g. Megabytes)\n  bs: binary short (e.g. MiB)\n  bl: binary long (e.g. Mebibytes) "
        )
    base = _BASE_1000 if fmt in {"ds", "dl"} else _BASE_1024
    units = {
        "ds": _UNITS_DECIMAL_SHORT,
        "dl": _UNITS_DECIMAL_LONG,
        "bs": _UNITS_BINARY_SHORT,
        "bl": _UNITS_BINARY_LONG,
    }.get(fmt, ["N/A"])
    index = 0
    size_: float = float(size)
    while size_ >= base and index < len(units) - 1:
        size_ /= base
        index += 1
    return f"{size_:.{precision}f} {units[index]}"


def parse_bytes(text: str, /) -> int:
    """Parse a human-readable byte size string into an integer number of bytes.

    The inverse of pretty_bytes. Accepts a number followed by an optional unit, e.g.
    "1.5 GiB" (1610612736), "1.54 KB" (1540) or "20 Megabytes" (20000000). Unit matching
    is case-insensitive and recognizes both decimal units (KB, Kilobytes, base 1000) and
    binary units (KiB, Kibibytes, base 1024). A bare number is interpreted as bytes.
    The result is rounded to the nearest integer.

    Parameters
    ----------
    text : str
        The human-readable size, e.g. "1.5 GiB".

    Returns
    -------
    int
        The size in bytes.

    Raises
    ------
    TypeError
        If text is not a string.
    ValueError
        If text cannot be parsed, the number is negative, or the unit is unknown.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")
    match = _PARSE_PATTERN.match(text.strip())
    if not match:
        raise ValueError(f"Cannot parse {text!r} as a byte size.")
    number_text = match.group("number")
    # Integers are parsed exactly (no float precision loss above 2**53).
    number: int | float
    if any(char in number_text for char in ".eE"):
        number = float(number_text)
        if not math.isfinite(number):
            raise ValueError(f"Cannot parse {text!r} as a byte size.")
    else:
        number = int(number_text)
    if number < 0:
        raise ValueError("Size must be non-negative.")
    unit = match.group("unit")
    multiplier = _UNIT_MULTIPLIERS.get(unit.lower(), 0) if unit else 1
    if not multiplier:
        raise ValueError(f"Unknown byte unit: {unit!r}.")
    return round(number * multiplier)

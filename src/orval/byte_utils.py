"""Utility functions for working with bytes."""

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

"""Utility functions for working with bytes."""

BASE_1000: int = 1000
BASE_1024: int = 1024

# Units decimal: base 1000
UNITS_DECIMAL_SHORT: list[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
UNITS_DECIMAL_LONG: list[str] = [
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
UNITS_BINARY_SHORT: list[str] = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]
UNITS_BINARY_LONG: list[str] = [
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

FORMATS: set[str] = {"decimal", "decimal-long", "binary", "binary-long"}


def format_bytes(size: int, /, fmt: str = "decimal", decimal_places: int = 2) -> str:
    """Convert a size in bytes to a human-readable string.

    Parameters
    ----------
    size_bytes : int
        The size in bytes.
    fmt : str
        The format to use. One of "decimal", "decimal-long", "binary", "binary-long"
    decimal_places : int
        The number of decimal places to round to..

    Returns
    -------
    str
        The formatted disk size as a human-readable string.
    """
    if size < 0:
        raise ValueError("Size must be a non-negative integer.")
    if fmt not in FORMATS:
        raise ValueError(f"Format must be one of {FORMATS}.")
    base = BASE_1000 if fmt in {"decimal", "decimal-long"} else BASE_1024
    units = {
        "decimal": UNITS_DECIMAL_SHORT,
        "decimal-long": UNITS_DECIMAL_LONG,
        "binary": UNITS_BINARY_SHORT,
        "binary-long": UNITS_BINARY_LONG,
    }.get(fmt, ["N/A"])
    index = 0
    size_: float = float(size)
    while size_ >= base and index < len(units) - 1:
        size_ /= base
        index += 1
    return f"{size_:.{decimal_places}f} {units[index]}"

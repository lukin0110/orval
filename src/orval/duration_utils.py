"""Utility functions for working with durations."""

# Unit factors expressed in microseconds, largest to smallest.
_UNITS: list[tuple[str, str, int]] = [
    ("d", "day", 86_400_000_000),
    ("h", "hour", 3_600_000_000),
    ("m", "minute", 60_000_000),
    ("s", "second", 1_000_000),
    ("ms", "millisecond", 1_000),
    ("µs", "microsecond", 1),
]

# short, long
_FORMATS: set[str] = {"s", "l"}


def pretty_duration(seconds: float, fmt: str = "s", /) -> str:
    """Convert a duration in seconds to a human-readable string.

    The duration is broken down into compound units (e.g., 9000 seconds becomes "2h 30m").
    Only non-zero components are shown, from largest to smallest. Sub-second durations are
    supported down to microseconds.

    Available formats:
    - s: short (e.g., 2h 30m)
    - l: long (e.g., 2 hours 30 minutes)

    Parameters
    ----------
    seconds : float
        The duration in seconds.
    fmt : str
        The format to use. One of "s", "l". Default is "s".

    Returns
    -------
    str
        The formatted duration as a human-readable string.
    """
    if not isinstance(seconds, int | float):
        raise TypeError("Duration must be a number.")
    if seconds < 0:
        raise ValueError("Duration must be non-negative.")
    if fmt not in _FORMATS:
        raise ValueError(
            f"Format must be one of {_FORMATS}.\n  s: short (e.g. 2h 30m)\n  l: long (e.g. 2 hours 30 minutes)"
        )
    total = round(seconds * 1_000_000)
    if total == 0:
        return "0s" if fmt == "s" else "0 seconds"
    parts: list[str] = []
    for short, long, factor in _UNITS:
        value, total = divmod(total, factor)
        if value:
            parts.append(f"{value}{short}" if fmt == "s" else f"{value} {long}{'s' if value != 1 else ''}")
    return " ".join(parts)

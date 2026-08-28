"""Utility functions for working with durations."""

import math
import re

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

# A single "<number><unit>" segment; the unit may be separated by whitespace or absent.
_SEGMENT_PATTERN: re.Pattern[str] = re.compile(r"(?P<number>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(?P<unit>[A-Za-zµμ]*)")


def _build_unit_factors() -> dict[str, int]:
    factors: dict[str, int] = {}
    for short, long, factor in _UNITS:
        factors[short] = factor
        factors[long] = factor
        factors[long + "s"] = factor
    # ASCII fallback and the Greek small mu (the micro sign normalizes differently across keyboards).
    factors["us"] = 1
    factors["μs"] = 1
    return factors


_UNIT_FACTORS: dict[str, int] = _build_unit_factors()


def _split_segments(text: str, /) -> list[tuple[str, str]]:
    """Split a duration string into (number, unit) segments, raising ValueError if unparseable."""
    stripped = text.strip()
    segments: list[tuple[str, str]] = []
    pos = 0
    while pos < len(stripped):
        match = _SEGMENT_PATTERN.match(stripped, pos)
        if not match:
            raise ValueError(f"Cannot parse {text!r} as a duration.")
        segments.append((match.group("number"), match.group("unit")))
        pos = match.end()
        while pos < len(stripped) and stripped[pos].isspace():
            pos += 1
    if not segments:
        raise ValueError(f"Cannot parse {text!r} as a duration.")
    return segments


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


def parse_duration(text: str, /) -> float:
    """Parse a human-readable duration string into a number of seconds.

    The inverse of pretty_duration. Accepts one or more number/unit segments, e.g.
    "1h30m" (5400.0), "2h 30m" (9000.0), "2 hours 30 minutes" (9000.0) or "250ms" (0.25).
    Unit matching is case-insensitive and recognizes both short units (d, h, m, s, ms, us
    and the micro-sign spelling of microseconds) and long units (days, hours, minutes,
    seconds, milliseconds, microseconds). A bare number is interpreted as seconds.
    The result is rounded to whole microseconds.

    Parameters
    ----------
    text : str
        The human-readable duration, e.g. "1h30m".

    Returns
    -------
    float
        The duration in seconds.

    Raises
    ------
    TypeError
        If text is not a string.
    ValueError
        If text cannot be parsed, the duration is negative, or a unit is unknown.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")
    segments = _split_segments(text)
    total: int | float = 0
    for number_text, unit in segments:
        # Integers are parsed exactly (no float precision loss above 2**53).
        number: int | float = float(number_text) if any(char in number_text for char in ".eE") else int(number_text)
        if number < 0:
            raise ValueError("Duration must be non-negative.")
        if not unit:
            if len(segments) > 1:
                raise ValueError(f"Cannot parse {text!r} as a duration: segment {number_text!r} is missing a unit.")
            factor = 1_000_000  # A bare number is interpreted as seconds.
        else:
            factor = _UNIT_FACTORS.get(unit.lower(), 0)
            if not factor:
                raise ValueError(f"Unknown duration unit: {unit!r}.")
        total += number * factor
    if isinstance(total, float) and not math.isfinite(total):
        raise ValueError(f"Cannot parse {text!r} as a duration.")
    return round(total) / 1_000_000

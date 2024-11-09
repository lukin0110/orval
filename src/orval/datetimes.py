"""Datetime utilities."""

import datetime


def utcnow() -> datetime.datetime:
    """Generate now as a datetime with UTC time zone info.

    The `datetime.datetime.utcnow()` function from the standard library does not include time zone information by
    default. https://docs.python.org/3/library/datetime.html#datetime.datetime.now
    """
    return datetime.datetime.now(tz=datetime.UTC)

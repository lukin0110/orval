"""Datetime utilities."""

import datetime


def utcnow() -> datetime.datetime:
    """Generate now as a datetime with UTC time zone info.

    The `datetime.datetime.utcnow()` function from the standard library does not include time zone information by
    default. https://docs.python.org/3/library/datetime.html#datetime.datetime.now
    """
    return datetime.datetime.now(tz=datetime.UTC)


def to_utc(value: datetime.datetime, *, assume_utc: bool = True) -> datetime.datetime:
    """Normalise a datetime to UTC.

    A naive datetime is assumed to already be in UTC and gets ``datetime.UTC`` attached; an
    aware datetime is converted with ``astimezone``. Pass ``assume_utc=False`` to raise on a
    naive value instead of guessing. A datetime counts as naive when its 'tzinfo' is ``None``
    or its 'utcoffset' returns ``None``, as in the standard library; ``astimezone`` would
    otherwise silently interpret it as system-local time.

    Parameters
    ----------
    value
        The datetime to normalise.
    assume_utc
        Whether a naive datetime is treated as UTC. When ``False``, a naive datetime raises.

    Returns
    -------
    datetime.datetime
        The same instant with ``datetime.UTC`` as its time zone.

    Raises
    ------
    ValueError
        If 'value' is naive and 'assume_utc' is ``False``.

    Examples
    --------
    >>> naive = datetime.datetime(2024, 1, 1, 12, 0)
    >>> to_utc(naive)
    datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    >>> cet = datetime.timezone(datetime.timedelta(hours=1))
    >>> to_utc(datetime.datetime(2024, 1, 1, 12, 0, tzinfo=cet))
    datetime.datetime(2024, 1, 1, 11, 0, tzinfo=datetime.timezone.utc)
    >>> to_utc(naive, assume_utc=False)
    Traceback (most recent call last):
        ...
    ValueError: Datetime must be timezone-aware.
    """
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        if not assume_utc:
            raise ValueError("Datetime must be timezone-aware.")
        return value.replace(tzinfo=datetime.UTC)
    return value.astimezone(datetime.UTC)

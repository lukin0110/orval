"""Datetime utilities."""

import datetime


def utcnow() -> datetime.datetime:
    """Generate now as a datetime with UTC time zone info.

    The `datetime.datetime.utcnow()` function from the standard library does not include time zone information by
    default. https://docs.python.org/3/library/datetime.html#datetime.datetime.now
    """
    return datetime.datetime.now(tz=datetime.UTC)


def _is_naive(value: datetime.datetime) -> bool:
    """Check whether a datetime lacks usable time zone information, as the standard library defines it."""
    return value.tzinfo is None or value.tzinfo.utcoffset(value) is None


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
    if not assume_utc and _is_naive(value):
        raise ValueError("Datetime must be timezone-aware.")
    return to_tz(value, datetime.UTC)


def to_tz(value: datetime.datetime, tz: datetime.tzinfo, *, assume: datetime.tzinfo | None = None) -> datetime.datetime:
    """Convert a datetime to the 'tz' time zone.

    An aware datetime is converted with ``astimezone``. A naive datetime is first assumed to be
    in 'assume', or in 'tz' itself when 'assume' is ``None``, in which case a time zone is
    attached without shifting the wall-clock time. A datetime counts as naive when its 'tzinfo'
    is ``None`` or its 'utcoffset' returns ``None``, as in the standard library; ``astimezone``
    would otherwise silently interpret it as system-local time. Naive values are always assumed,
    so both 'tz' and 'assume' must report a UTC offset. Ambiguous and non-existent local times,
    around a daylight saving transition, follow the standard library's ``fold`` attribute.

    Parameters
    ----------
    value
        The datetime to convert.
    tz
        The target time zone, for example ``zoneinfo.ZoneInfo("Europe/Brussels")``.
    assume
        The time zone a naive 'value' is assumed to be in. Defaults to 'tz'.

    Returns
    -------
    datetime.datetime
        The same instant expressed in 'tz'.

    Examples
    --------
    >>> cet = datetime.timezone(datetime.timedelta(hours=1))
    >>> to_tz(datetime.datetime(2024, 1, 1, 12, 0), cet)
    datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    >>> to_tz(datetime.datetime(2024, 1, 1, 12, 0), datetime.UTC, assume=cet)
    datetime.datetime(2024, 1, 1, 11, 0, tzinfo=datetime.timezone.utc)
    >>> to_tz(datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.UTC), cet)
    datetime.datetime(2024, 1, 1, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))
    """
    if _is_naive(value):
        value = value.replace(tzinfo=tz if assume is None else assume)
    return value.astimezone(tz)

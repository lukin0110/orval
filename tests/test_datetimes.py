"""Tests for the datetime utilities."""

import datetime

import pytest

from orval import to_utc

NAIVE = datetime.datetime(2024, 1, 1, 12, 0)


class _NoOffset(datetime.tzinfo):
    """A tzinfo with an unknown offset, which the standard library treats as naive."""

    def utcoffset(self, dt: datetime.datetime | None) -> None:
        return None

    def dst(self, dt: datetime.datetime | None) -> None:
        return None

    def tzname(self, dt: datetime.datetime | None) -> str:
        return "Unknown"


def test_to_utc_naive() -> None:
    """Should attach UTC to a naive datetime without shifting the wall-clock time."""
    result = to_utc(NAIVE)
    assert result.tzinfo is datetime.UTC
    assert result == NAIVE.replace(tzinfo=datetime.UTC)


@pytest.mark.parametrize(
    ("offset", "expected_hour", "expected_minute"),
    [
        (datetime.timedelta(0), 12, 0),
        (datetime.timedelta(hours=1), 11, 0),
        (datetime.timedelta(hours=-5), 17, 0),
        (datetime.timedelta(hours=5, minutes=30), 6, 30),
    ],
)
def test_to_utc_aware(offset: datetime.timedelta, expected_hour: int, expected_minute: int) -> None:
    """Should convert an aware datetime to the same instant in UTC."""
    value = NAIVE.replace(tzinfo=datetime.timezone(offset))
    result = to_utc(value)
    assert result.tzinfo is datetime.UTC
    assert result == value
    assert (result.hour, result.minute) == (expected_hour, expected_minute)


def test_to_utc_aware_not_assumed() -> None:
    """Should still convert an aware datetime when naive values may not be assumed UTC."""
    value = NAIVE.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=1)))
    result = to_utc(value, assume_utc=False)
    assert result.tzinfo is datetime.UTC
    assert result == value


def test_to_utc_naive_not_assumed() -> None:
    """Should raise a ValueError for a naive datetime when it may not be assumed UTC."""
    with pytest.raises(ValueError, match=r"Datetime must be timezone-aware."):
        to_utc(NAIVE, assume_utc=False)


def test_to_utc_tzinfo_without_offset() -> None:
    """Should treat a tzinfo without a UTC offset as naive."""
    value = NAIVE.replace(tzinfo=_NoOffset())
    assert to_utc(value) == NAIVE.replace(tzinfo=datetime.UTC)
    with pytest.raises(ValueError, match=r"Datetime must be timezone-aware."):
        to_utc(value, assume_utc=False)

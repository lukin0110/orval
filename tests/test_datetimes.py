"""Tests for the datetime utilities."""

import datetime
import zoneinfo

import pytest

from orval import to_tz, to_utc

NAIVE = datetime.datetime(2024, 1, 1, 12, 0)
BRUSSELS = zoneinfo.ZoneInfo("Europe/Brussels")


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


@pytest.mark.parametrize(
    ("value", "expected_offset"),
    [
        (datetime.datetime(2024, 1, 15, 9, 0), datetime.timedelta(hours=1)),
        (datetime.datetime(2024, 7, 15, 9, 0), datetime.timedelta(hours=2)),
    ],
)
def test_to_tz_naive_defaults_to_target(value: datetime.datetime, expected_offset: datetime.timedelta) -> None:
    """Should attach the target time zone to a naive datetime without shifting the wall-clock time."""
    result = to_tz(value, BRUSSELS)
    assert result.tzinfo is BRUSSELS
    assert result.replace(tzinfo=None) == value
    assert result.utcoffset() == expected_offset


@pytest.mark.parametrize(
    ("value", "expected_hour"),
    [
        (datetime.datetime(2024, 1, 15, 9, 0), 8),
        (datetime.datetime(2024, 7, 15, 9, 0), 7),
    ],
)
def test_to_tz_naive_assumed_across_dst(value: datetime.datetime, expected_hour: int) -> None:
    """Should read a naive datetime in 'assume' and convert it, following that zone's daylight saving rules."""
    result = to_tz(value, datetime.UTC, assume=BRUSSELS)
    assert result.tzinfo is datetime.UTC
    assert result.hour == expected_hour
    assert result == value.replace(tzinfo=BRUSSELS)


@pytest.mark.parametrize(
    ("value", "expected_hour"),
    [
        (datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.UTC), 13),
        (datetime.datetime(2024, 7, 1, 12, 0, tzinfo=datetime.UTC), 14),
    ],
)
def test_to_tz_aware_conversion(value: datetime.datetime, expected_hour: int) -> None:
    """Should convert an aware datetime to the same instant read in the target time zone."""
    result = to_tz(value, BRUSSELS)
    assert result.tzinfo is BRUSSELS
    assert result == value
    assert result.hour == expected_hour


@pytest.mark.parametrize(
    ("offset", "expected_hour", "expected_minute"),
    [
        (datetime.timedelta(0), 12, 0),
        (datetime.timedelta(hours=1), 11, 0),
        (datetime.timedelta(hours=-5), 17, 0),
        (datetime.timedelta(hours=5, minutes=30), 6, 30),
    ],
)
def test_to_tz_aware_fixed_offsets(offset: datetime.timedelta, expected_hour: int, expected_minute: int) -> None:
    """Should convert a fixed-offset datetime the same way 'to_utc' does."""
    value = NAIVE.replace(tzinfo=datetime.timezone(offset))
    result = to_tz(value, datetime.UTC)
    assert result.tzinfo is datetime.UTC
    assert result == value
    assert (result.hour, result.minute) == (expected_hour, expected_minute)


def test_to_tz_aware_ignores_assume() -> None:
    """Should ignore 'assume' for an aware datetime, which already knows its own time zone."""
    value = NAIVE.replace(tzinfo=datetime.UTC)
    assert to_tz(value, datetime.UTC, assume=BRUSSELS) == value


@pytest.mark.parametrize(("fold", "expected_hour"), [(0, 0), (1, 1)])
def test_to_tz_ambiguous_local_time(fold: int, expected_hour: int) -> None:
    """Should resolve a local time that occurs twice through the standard library's 'fold' attribute."""
    value = datetime.datetime(2024, 10, 27, 2, 30, fold=fold)
    result = to_tz(value, datetime.UTC, assume=BRUSSELS)
    assert (result.hour, result.minute) == (expected_hour, 30)


def test_to_tz_nonexistent_local_time() -> None:
    """Should resolve a local time skipped by a daylight saving jump the way the standard library does."""
    value = datetime.datetime(2024, 3, 31, 2, 30)
    result = to_tz(value, datetime.UTC, assume=BRUSSELS)
    assert (result.hour, result.minute) == (1, 30)


def test_to_tz_tzinfo_without_offset() -> None:
    """Should treat a tzinfo without a UTC offset as naive, as 'to_utc' does."""
    value = NAIVE.replace(tzinfo=_NoOffset())
    assert to_tz(value, BRUSSELS) == NAIVE.replace(tzinfo=BRUSSELS)


def test_to_tz_round_trips_with_to_utc() -> None:
    """Should read a UTC datetime back as local wall-clock time."""
    value = datetime.datetime(2024, 7, 15, 9, 0)
    assert to_tz(to_utc(value, assume_utc=True), BRUSSELS).hour == 11

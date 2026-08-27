"""Tests for the coercion functions."""

import math

import pytest

from orval import safe_float, safe_int, to_bool


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("t", True),
        ("yes", True),
        ("Yes", True),
        ("y", True),
        ("on", True),
        ("ON", True),
        ("1", True),
        ("  yes  ", True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("f", False),
        ("no", False),
        ("n", False),
        ("off", False),
        ("Off", False),
        ("0", False),
        ("  off  ", False),
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        (1.0, True),
        (0.0, False),
    ],
)
def test_to_bool(value: object, expected: bool) -> None:
    """Should convert recognized values to a boolean."""
    assert to_bool(value) is expected


@pytest.mark.parametrize(
    "value",
    ["", "maybe", "yess", "2", "-1", 2, -1, 0.5, None, [], {}],
)
def test_to_bool_unrecognized(value: object) -> None:
    """Should raise a ValueError for unrecognized values without a default."""
    with pytest.raises(ValueError, match="Cannot convert"):
        to_bool(value)


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        ("maybe", True, True),
        ("maybe", False, False),
        (None, True, True),
        ("", False, False),
        ("yes", False, True),
        ("off", True, False),
    ],
)
def test_to_bool_default(value: object, default: bool, expected: bool) -> None:
    """Should return the default for unrecognized values."""
    assert to_bool(value, default=default) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("42", 42),
        ("-7", -7),
        ("  42  ", 42),
        ("3.7", 3),
        ("-3.7", -3),
        ("1e3", 1000),
        (42, 42),
        (3.9, 3),
        (-3.9, -3),
        (True, 1),
        (False, 0),
    ],
)
def test_safe_int(value: object, expected: int) -> None:
    """Should convert values to an integer."""
    assert safe_int(value) == expected


@pytest.mark.parametrize(
    "value",
    ["", "abc", "1.2.3", "nan", "inf", None, [], {}],
)
def test_safe_int_default(value: object) -> None:
    """Should return the default when conversion fails."""
    assert safe_int(value) is None
    assert safe_int(value, default=0) == 0
    assert safe_int(value, default=-1) == -1


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3.5", 3.5),
        ("-0.5", -0.5),
        ("  2.5  ", 2.5),
        ("42", 42.0),
        ("1e-3", 0.001),
        (42, 42.0),
        (math.pi, math.pi),
        (True, 1.0),
        ("inf", math.inf),
    ],
)
def test_safe_float(value: object, expected: float) -> None:
    """Should convert values to a float."""
    assert safe_float(value) == expected


@pytest.mark.parametrize(
    "value",
    ["", "abc", "1.2.3", None, [], {}],
)
def test_safe_float_default(value: object) -> None:
    """Should return the default when conversion fails."""
    assert safe_float(value) is None
    assert safe_float(value, default=0.0) == pytest.approx(0.0)
    assert safe_float(value, default=-1.5) == pytest.approx(-1.5)

"""Tests for the misc utility functions."""

from collections.abc import Callable

import pytest

from orval import coalesce, coalesce_lazy


def test_coalesce_returns_first_non_none() -> None:
    """Should return the first value that is not None."""
    assert coalesce(None, None, 3, 5) == 3
    assert coalesce("a", "b") == "a"


def test_coalesce_keeps_falsy_values() -> None:
    """Should keep falsy values such as 0, empty string, and False."""
    assert coalesce(None, 0, 5) == 0
    assert coalesce(None, "", "fallback") == ""  # ruff: ignore[compare-to-empty-string] — the exact empty string must be kept
    assert coalesce(None, False, True) is False
    assert coalesce(None, [], [1]) == []


def test_coalesce_all_none() -> None:
    """Should return None when all values are None."""
    assert coalesce() is None
    assert coalesce(None) is None
    assert coalesce(None, None, None) is None


def test_coalesce_fallback_as_last_argument() -> None:
    """Should return a constant fallback passed as the last argument only when needed."""
    assert coalesce(None, None, 8080) == 8080
    assert coalesce(None, 3000, 8080) == 3000


def test_coalesce_lazy_returns_first_non_none() -> None:
    """Should return the first callable's result that is not None."""
    assert coalesce_lazy(lambda: None, lambda: 3, lambda: 5) == 3
    assert coalesce_lazy(lambda: 0, lambda: 5) == 0


def test_coalesce_lazy_short_circuits() -> None:
    """Should not invoke callables after the first non-None result."""
    calls: list[str] = []

    def make(name: str, value: int | None) -> Callable[[], int | None]:
        def _producer() -> int | None:
            calls.append(name)
            return value

        return _producer

    assert coalesce_lazy(make("a", None), make("b", 2), make("c", 3)) == 2
    assert calls == ["a", "b"]


def test_coalesce_lazy_all_none() -> None:
    """Should return None when all callables return None."""
    assert coalesce_lazy() is None
    assert coalesce_lazy(lambda: None, lambda: None) is None
    assert coalesce_lazy(lambda: None, lambda: 8080) == 8080


def test_coalesce_lazy_propagates_errors() -> None:
    """Should propagate exceptions raised by an invoked callable."""

    def boom() -> int | None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        coalesce_lazy(lambda: None, boom)
    # A callable after a non-None result is never invoked, so it does not raise.
    assert coalesce_lazy(lambda: 1, boom) == 1

"""Tests for the misc utility functions."""

import asyncio
import inspect
import logging
from collections.abc import Callable
from pathlib import Path
from typing import assert_type

import pytest

from orval import coalesce, coalesce_lazy, timing


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


def test_coalesce_narrows_return_type_with_non_none_fallback() -> None:
    """Should type the result as ``T`` rather than ``T | None`` when the last value cannot be None.

    The ``assert_type`` calls are no-ops at runtime; ``ty check`` verifies them statically.
    """

    def check(maybe: Path | None, fallback: Path) -> Path:
        assert_type(coalesce(fallback), Path)
        assert_type(coalesce(maybe, fallback), Path)
        assert_type(coalesce(maybe, maybe, maybe, maybe, fallback), Path)
        # The last value may be None, so the result may be None too.
        assert_type(coalesce(maybe, maybe), Path | None)
        assert_type(coalesce(maybe, None), Path | None)
        # A chain longer than five values falls back to the variadic signature.
        assert_type(coalesce(maybe, maybe, maybe, maybe, maybe, fallback), Path | None)
        # Under a strict type checker this return only passes because the result is a ``Path``.
        return coalesce(maybe, fallback)

    assert check(None, Path("/srv")) == Path("/srv")
    assert check(Path("/home"), Path("/srv")) == Path("/home")


def test_coalesce_lazy_narrows_return_type_with_non_none_fallback() -> None:
    """Should type the result as ``T`` rather than ``T | None`` when the last callable cannot return None.

    The ``assert_type`` calls are no-ops at runtime; ``ty check`` verifies them statically.
    """

    def check(maybe: Path | None, from_env: Callable[[], Path | None], fallback: Path) -> Path:
        assert_type(coalesce_lazy(lambda: fallback), Path)
        assert_type(coalesce_lazy(lambda: maybe, lambda: fallback), Path)
        assert_type(coalesce_lazy(lambda: maybe, from_env, from_env, from_env, lambda: fallback), Path)
        # The last callable may return None, so the result may be None too.
        assert_type(coalesce_lazy(lambda: maybe, from_env), Path | None)
        assert_type(coalesce_lazy(from_env), Path | None)
        # A chain longer than five callables falls back to the variadic signature.
        assert_type(coalesce_lazy(from_env, from_env, from_env, from_env, from_env, lambda: fallback), Path | None)
        # Under a strict type checker this return only passes because the result is a ``Path``.
        return coalesce_lazy(lambda: maybe, from_env, lambda: fallback)

    assert check(None, lambda: None, Path("/srv")) == Path("/srv")
    assert check(None, lambda: Path("/env"), Path("/srv")) == Path("/env")
    assert check(Path("/home"), lambda: Path("/env"), Path("/srv")) == Path("/home")


def test_timing_sync(caplog: pytest.LogCaptureFixture) -> None:
    """Should return the wrapped function's result and log the elapsed time at INFO."""

    @timing
    def add(a: int, b: int) -> int:
        return a + b

    with caplog.at_level(logging.INFO, logger="orval.utils"):
        assert add(1, b=2) == 3
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.INFO
    assert "Timing for 'add':" in caplog.records[0].message


def test_timing_sync_with_level(caplog: pytest.LogCaptureFixture) -> None:
    """Should log at the level passed to the decorator."""

    @timing(level=logging.DEBUG)
    def noop() -> None:
        return None

    with caplog.at_level(logging.DEBUG, logger="orval.utils"):
        assert noop() is None
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.DEBUG
    assert "Timing for 'noop':" in caplog.records[0].message


def test_timing_async(caplog: pytest.LogCaptureFixture) -> None:
    """Should await the wrapped coroutine function and log the elapsed time at INFO."""

    @timing
    async def add(a: int, b: int) -> int:
        await asyncio.sleep(0)
        return a + b

    assert inspect.iscoroutinefunction(add)
    with caplog.at_level(logging.INFO, logger="orval.utils"):
        assert asyncio.run(add(1, b=2)) == 3
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.INFO
    assert "Timing for 'add':" in caplog.records[0].message


def test_timing_async_with_level(caplog: pytest.LogCaptureFixture) -> None:
    """Should log at the level passed to the decorator for coroutine functions."""

    @timing(level=logging.DEBUG)
    async def noop() -> None:
        await asyncio.sleep(0)

    assert inspect.iscoroutinefunction(noop)
    with caplog.at_level(logging.DEBUG, logger="orval.utils"):
        assert asyncio.run(noop()) is None
    assert len(caplog.records) == 1
    assert caplog.records[0].levelno == logging.DEBUG
    assert "Timing for 'noop':" in caplog.records[0].message


def test_timing_async_includes_await_time(caplog: pytest.LogCaptureFixture) -> None:
    """Should measure the time spent awaiting, not just the time to create the coroutine."""

    @timing
    async def slow() -> None:
        await asyncio.sleep(0.05)

    with caplog.at_level(logging.INFO, logger="orval.utils"):
        asyncio.run(slow())
    assert len(caplog.records) == 1
    elapsed = float(caplog.records[0].message.split(": ")[1].removesuffix("s"))
    # The logged value is rounded to 3 decimals, so allow for rounding down by up to 0.001.
    assert elapsed >= 0.05 - 0.001

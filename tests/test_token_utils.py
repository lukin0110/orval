"""Tests for the token estimation functions."""

import pytest

from orval import estimate_tokens, truncate_tokens

PROSE = "The quick brown fox jumps over the lazy dog. " * 10
CODE = 'def greet(name: str) -> str:\n    return f"Hello {name}"\n' * 10


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", 0),
        ("hello", 1),
        ("hello world", 3),
        ("Hello world, how are you?", 7),
        ("Will this prompt fit in the context window?", 11),
        ("The quick brown fox jumps over the lazy dog.", 12),
        # Whitespace still tokenizes.
        ("   ", 1),
        ("\n\n\n\n\n\n\n\n", 2),
        # Word-heavy text is driven by the ~0.75 words per token estimate.
        ("word " * 100, 133),
        # Code-like text is detected and estimated at ~3 characters per token.
        ('def greet(name: str) -> str:\n    return f"Hello {name}"', 18),
        ('{"key": "value", "items": [1, 2, 3]}', 12),
    ],
)
def test_estimate_tokens(text: str, expected: int) -> None:
    """Should estimate the number of tokens in a text."""
    assert estimate_tokens(text) == expected


def test_estimate_tokens_code_denser_than_prose() -> None:
    """Should estimate more tokens for code than for prose of the same length."""
    length = min(len(PROSE), len(CODE))
    assert estimate_tokens(CODE[:length]) > estimate_tokens(PROSE[:length])


@pytest.mark.parametrize(
    ("text", "budget", "expected"),
    [
        # Text that already fits is returned unchanged.
        ("hello world", 100, "hello world"),
        ("", 5, ""),
        # Truncation cuts at a word boundary and strips trailing whitespace.
        ("The quick brown fox jumps over the lazy dog.", 5, "The quick brown fox"),
        ("The quick brown fox jumps over the lazy dog.", 1, "The"),
        # A single unbroken word is cut mid-word rather than dropped entirely.
        ("supercalifragilistic", 1, "super"),
        ("hello", 1, "hello"),
    ],
)
def test_truncate_tokens(text: str, budget: int, expected: str) -> None:
    """Should truncate a text to fit within a token budget."""
    assert truncate_tokens(text, budget) == expected


@pytest.mark.parametrize("text", [PROSE, CODE])
@pytest.mark.parametrize("budget", [1, 5, 12, 50, 10_000])
def test_truncate_tokens_respects_budget(text: str, budget: int) -> None:
    """Should return a prefix whose estimate fits the budget, keeping all text that fits."""
    truncated = truncate_tokens(text, budget)
    assert estimate_tokens(truncated) <= budget
    assert text.startswith(truncated) or text == truncated
    if estimate_tokens(text) <= budget:
        assert truncated == text


@pytest.mark.parametrize("budget", [0, -1])
def test_truncate_tokens_invalid_budget(budget: int) -> None:
    """Should raise a ValueError for a non-positive budget."""
    with pytest.raises(ValueError, match=r"Budget must be a positive integer."):
        truncate_tokens("hello world", budget)

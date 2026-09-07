"""Utility functions for estimating LLM token counts.

Exact token counts depend on the tokenizer of the model in use (tiktoken, SentencePiece, etc.).
These helpers use the widely cited rule of thumb that one token is roughly 4 characters or
roughly 0.75 words of English text, with a denser ratio for source code. That makes them
suitable for "will this fit in the context window" guards and log/prompt trimming without
pulling in a tokenizer dependency, but not for billing or hard limits.
"""

import re

# Rule of thumb for English prose: one token is about 4 characters, or about 0.75 words.
_TEXT_CHARS_PER_TOKEN: float = 4.0
_WORDS_PER_TOKEN: float = 0.75
# Code tokenizes denser than prose: identifiers, punctuation and indentation split into more
# tokens, averaging closer to 3 characters per token.
_CODE_CHARS_PER_TOKEN: float = 3.0

# Characters that are common in source code (and structured data) but rare in prose.
_CODE_CHARS: frozenset[str] = frozenset("{}[]()<>;:=_#/\\|~^&*%$@`+")
# Fraction of code characters above which a text is treated as code.
_CODE_DENSITY_THRESHOLD: float = 0.05

_WORD_RE: re.Pattern[str] = re.compile(r"\S+")


def _chars_per_token(text: str) -> float:
    """Pick the characters-per-token ratio based on how code-like the text is."""
    density = sum(char in _CODE_CHARS for char in text) / len(text)
    return _CODE_CHARS_PER_TOKEN if density >= _CODE_DENSITY_THRESHOLD else _TEXT_CHARS_PER_TOKEN


def _estimate(text: str, chars_per_token: float) -> int:
    """Estimate tokens for a non-empty text with a fixed characters-per-token ratio.

    Takes the larger of the character-based and word-based estimates (rounded half up),
    so the guard errs toward overestimating.
    """
    char_estimate = len(text) / chars_per_token
    word_estimate = sum(1 for _ in _WORD_RE.finditer(text)) / _WORDS_PER_TOKEN
    return max(1, int(max(char_estimate, word_estimate) + 0.5))


def estimate_tokens(text: str) -> int:
    """Estimate the number of LLM tokens in a text.

    Uses a heuristic of ~4 characters or ~0.75 words per token for prose, and ~3 characters
    per token for code-like text (detected by the density of characters such as braces,
    brackets and operators). The two estimates are combined by taking the larger one, so the
    result leans toward overestimating: ideal for context-window guards, not for billing.

    Parameters
    ----------
    text
        The text to estimate the token count for.

    Returns
    -------
    int
        The estimated number of tokens. Empty text yields 0.
    """
    if not text:
        return 0
    return _estimate(text, _chars_per_token(text))


def truncate_tokens(text: str, budget: int, /) -> str:
    """Truncate a text so its estimated token count fits within a budget.

    Uses the same heuristic as 'estimate_tokens', so the returned text satisfies
    ``estimate_tokens(result) <= budget``. If the text already fits, it is returned
    unchanged. When a cut is needed, it backs off to the previous word boundary (unless the
    text is a single unbroken word) and strips trailing whitespace.

    Parameters
    ----------
    text
        The text to truncate.
    budget
        The maximum number of (estimated) tokens the result may contain.

    Returns
    -------
    str
        The largest prefix of the text that fits within the token budget.

    Raises
    ------
    ValueError
        If 'budget' is not a positive integer.
    """
    if budget <= 0:
        raise ValueError("Budget must be a positive integer.")
    if not text:
        return text
    chars_per_token = _chars_per_token(text)
    if _estimate(text, chars_per_token) <= budget:
        return text
    # Binary search for the longest prefix that fits. The estimate is monotonic in the prefix
    # length (both the character count and the word count only grow), and the code/prose ratio
    # is fixed up front so the classification cannot flip mid-search.
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if _estimate(text[:middle], chars_per_token) <= budget:
            low = middle
        else:
            high = middle - 1
    truncated = text[:low]
    # Avoid ending mid-word: back off to the last whitespace when the cut splits a word.
    if truncated and not truncated[-1].isspace() and not text[low].isspace():
        boundary = re.search(r"\s+\S+$", truncated)
        if boundary is not None:
            truncated = truncated[: boundary.start()]
    return truncated.rstrip()

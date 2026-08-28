"""Tests for the string manipulation functions."""

import pytest
from typeguard import suppress_type_checks

from orval import (
    camel_case,
    dot_case,
    kebab_case,
    mask,
    pascal_case,
    slugify,
    snake_case,
    strip_accents,
    strip_styling,
    train_case,
    truncate,
)


@pytest.mark.parametrize(
    ("string", "scream", "expected"),
    [
        ("great scott", False, "great-scott"),
        ("Great Scott", False, "great-scott"),
        ("great.scott", False, "great-scott"),
        ("Great.Scott", False, "great-scott"),
        ("great_scott", False, "great-scott"),
        ("Great_Scott", False, "great-scott"),
        ("_", False, ""),
        ("_C", False, "c"),
        ("great    scott", False, "great-scott"),
        ("Great    Scott", False, "great-scott"),
        ("!!Great    Scott!!", False, "great-scott"),
        ("great", False, "great"),
        ("hello world again", False, "hello-world-again"),
        ("  great   scott  ", False, "great-scott"),
        ("GREAT SCOTT", False, "great-scott"),
        ("GREAT SCOTT", True, "GREAT-SCOTT"),
        ("", False, ""),
        ("", True, ""),
        ("single", False, "single"),
        ("multiple words in a string", False, "multiple-words-in-a-string"),
        ("!!", False, ""),
        ("great scott", True, "GREAT-SCOTT"),
        ("Great Scott", True, "GREAT-SCOTT"),
        ("hello", True, "HELLO"),
        ("hello world again", True, "HELLO-WORLD-AGAIN"),
        ("  great   scott  ", True, "GREAT-SCOTT"),
        ("single", True, "SINGLE"),
        ("multiple words in a string", True, "MULTIPLE-WORDS-IN-A-STRING"),
        ("!!öì 💩", True, "ÖÌ"),
        ("!!ö ì 💩", True, "Ö-Ì"),
        ("こんにちは世界", True, "こんにちは世界"),
        ("こんにちは世界", False, "こんにちは世界"),
        ("Hello 世界", True, "HELLO-世界"),
        ("Hello 世界", False, "hello-世界"),
        ("Hello 世界 W", False, "hello-世界-w"),
    ],
)
def test_kebab_case(string: str, scream: bool, expected: str) -> None:
    """Should convert a string to kebab-case."""
    assert kebab_case(string, scream) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("Hello World", "hello-world"),
        ("Hello world", "hello-world"),
        ("Héllo Wörld", "hello-world"),
        ("Hello.World", "hello-world"),
        ("Hello.world", "hello-world"),
        ("Hello-World", "hello-world"),
        ("Hello-world", "hello-world"),
        ("Hello   World", "hello-world"),
        ("Hello   world", "hello-world"),
        ("Hello_World", "hello-world"),
        ("Hello_world", "hello-world"),
        ("", ""),
        ("    ", ""),
        ("!!Hello World!!", "hello-world"),
        ("こんにちは世界", ""),
        ("Hello 世界", "hello"),
        ("Hello 世界-W", "hello-w"),
        ("!!", ""),
        ("!!öì 💩", "oi"),
        ("!!ö ì 💩", "o-i"),
    ],
)
def test_slugify(string: str, expected: str) -> None:
    """Should create a slug from a given string."""
    assert slugify(string) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("great scott", "greatScott"),
        ("Great Scott", "greatScott"),
        ("great", "great"),
        ("hello world again", "helloWorldAgain"),
        ("  great   scott  ", "greatScott"),
        ("GREAT SCOTT", "greatScott"),
        ("", ""),
        ("single", "single"),
        ("multiple words in a string", "multipleWordsInAString"),
        ("!!", ""),
        ("!!öì 💩", "öì"),
        ("!!ö ì 💩", "öÌ"),
    ],
)
def test_camel_case(string: str, expected: str) -> None:
    """Should convert a string to camelCase."""
    assert camel_case(string) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("great scott", "GreatScott"),
        ("Great Scott", "GreatScott"),
        ("great", "Great"),
        ("hello world again", "HelloWorldAgain"),
        ("  great   scott  ", "GreatScott"),
        ("GREAT SCOTT", "GreatScott"),
        ("", ""),
        ("single", "Single"),
        ("multiple words in a string", "MultipleWordsInAString"),
        ("!!", ""),
        ("!!öì 💩", "Öì"),
        ("!!ö ì 💩", "ÖÌ"),
    ],
)
def test_pascal_case(string: str, expected: str) -> None:
    """Should convert a string to PascalCase."""
    assert pascal_case(string) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("great scott", "Great-Scott"),
        ("Great Scott", "Great-Scott"),
        ("great", "Great"),
        ("hello world again", "Hello-World-Again"),
        ("  great   scott  ", "Great-Scott"),
        ("GREAT SCOTT", "Great-Scott"),
        ("", ""),
        ("single", "Single"),
        ("multiple words in a string", "Multiple-Words-In-A-String"),
        ("!!", ""),
        ("!!öì 💩", "Öì"),
        ("!!ö ì 💩", "Ö-Ì"),
    ],
)
def test_train_case(string: str, expected: str) -> None:
    """Should convert a string to train-case."""
    assert train_case(string, unicode=True) == expected


@pytest.mark.parametrize(
    ("string", "scream", "expected"),
    [
        ("great scott", False, "great_scott"),
        ("Great Scott", False, "great_scott"),
        ("great", False, "great"),
        ("hello world again", False, "hello_world_again"),
        ("  great   scott  ", False, "great_scott"),
        ("GREAT SCOTT", False, "great_scott"),
        ("GREAT SCOTT", True, "GREAT_SCOTT"),
        ("", False, ""),
        ("", True, ""),
        ("single", False, "single"),
        ("multiple words in a string", False, "multiple_words_in_a_string"),
        ("!!", False, ""),
        ("great scott", True, "GREAT_SCOTT"),
        ("Great Scott", True, "GREAT_SCOTT"),
        ("hello", True, "HELLO"),
        ("hello world again", True, "HELLO_WORLD_AGAIN"),
        ("  great   scott  ", True, "GREAT_SCOTT"),
        ("single", True, "SINGLE"),
        ("multiple words in a string", True, "MULTIPLE_WORDS_IN_A_STRING"),
        ("!!öì 💩", True, "ÖÌ"),
        ("!!ö ì 💩", True, "Ö_Ì"),
    ],
)
def test_snake_case(string: str, scream: bool, expected: str) -> None:
    """Should convert a string to snake_case."""
    assert snake_case(string, scream) == expected


@pytest.mark.parametrize(
    ("string", "scream", "expected"),
    [
        ("great scott", False, "great.scott"),
        ("Great Scott", False, "great.scott"),
        ("great", False, "great"),
        ("hello world again", False, "hello.world.again"),
        ("  great   scott  ", False, "great.scott"),
        ("GREAT SCOTT", False, "great.scott"),
        ("GREAT SCOTT", True, "GREAT.SCOTT"),
        ("", False, ""),
        ("", True, ""),
        ("single", False, "single"),
        ("multiple words in a string", False, "multiple.words.in.a.string"),
        ("!!", False, ""),
        ("great scott", True, "GREAT.SCOTT"),
        ("Great Scott", True, "GREAT.SCOTT"),
        ("hello", True, "HELLO"),
        ("hello world again", True, "HELLO.WORLD.AGAIN"),
        ("  great   scott  ", True, "GREAT.SCOTT"),
        ("single", True, "SINGLE"),
        ("multiple words in a string", True, "MULTIPLE.WORDS.IN.A.STRING"),
        ("!!öì 💩", True, "ÖÌ"),
        ("!!ö ì 💩", True, "Ö.Ì"),
    ],
)
def test_dot_case(string: str, scream: bool, expected: str) -> None:
    """Should convert a string to dot.case."""
    assert dot_case(string, scream) == expected


@pytest.mark.parametrize(
    ("string", "number", "suffix", "expected"),
    [
        ("hello world", 5, "...", "hell..."),
        ("hello world", 11, "...", "hello world"),
        ("hello world", 12, "...", "hello world"),
        ("hello world", 0, "...", ValueError),
        ("hello world", -1, "...", ValueError),
        ("hello world", 5, "--", "hell--"),
        ("hello", 5, "...", "hello"),
        ("hello", 4, "...", "hel..."),
        ("", 5, "...", ""),
        ("a", 1, "...", "a"),
        ("a", 2, "...", "a"),
    ],
)
def test_truncate(string: str, number: int, suffix: str, expected: str | type[ValueError]) -> None:
    """Should truncate a string to a certain number of characters."""
    if expected is ValueError:
        with pytest.raises(ValueError, match=r"Number must be a positive integer."):
            truncate(string, number, suffix)
    else:
        assert truncate(string, number, suffix) == expected


@pytest.mark.parametrize(
    ("string", "show", "side", "mask_char", "expected"),
    [
        ("secret", 4, "r", "*", "**cret"),
        ("secret", 4, "l", "*", "secr**"),
        ("sk-abc123xyz", 4, "r", "*", "********3xyz"),
        ("sk-abc123xyz", 4, "l", "*", "sk-a********"),
        ("4111111111111111", 4, "r", "*", "************1111"),
        ("secret", 2, "r", "#", "####et"),
        ("secret", 0, "r", "*", "******"),
        ("secret", 0, "l", "*", "******"),
    ],
)
def test_mask(string: str, show: int, side: str, mask_char: str, expected: str) -> None:
    """Should mask a string while keeping a few characters visible."""
    assert mask(string, show=show, side=side, mask_char=mask_char) == expected


@pytest.mark.parametrize(
    ("string", "show", "expected"),
    [
        ("abc", 4, "***"),
        ("abcd", 4, "****"),
        ("secret", 6, "******"),
        ("secret", 100, "******"),
        ("", 4, ""),
    ],
)
def test_mask_short_input(string: str, show: int, expected: str) -> None:
    """Should fully mask strings that are too short to safely reveal characters."""
    assert mask(string, show=show) == expected


def test_mask_invalid() -> None:
    """Should raise a ValueError for a negative 'show' or an unrecognized 'side'."""
    with pytest.raises(ValueError, match=r"Show must be a non-negative integer."):
        mask("secret", show=-1)
    with pytest.raises(ValueError, match=r"Side must be one of"):
        mask("secret", side="x")
    with pytest.raises(ValueError, match=r"Mask char must be a single character."):
        mask("secret", mask_char="")
    with pytest.raises(ValueError, match=r"Mask char must be a single character."):
        mask("secret", mask_char="##")


@suppress_type_checks
def test_mask_invalid_type() -> None:
    """Should raise a TypeError when the input is not a string."""
    with pytest.raises(TypeError, match=r"Value must be a string."):
        mask(12345)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("hello", "hello"),
        ("", ""),
        ("café", "cafe"),
        ("Héllo Wörld", "Hello World"),
        ("naïve façade", "naive facade"),
        ("Ĝis reĝis, ĉu ŝanĝiĝis?", "Gis regis, cu sangigis?"),
        # Decomposed input ('e' followed by a combining acute accent).
        ("cafe\u0301", "cafe"),
        # Non-Latin scripts are preserved, unlike 'slugify'.
        ("こんにちは世界", "こんにちは世界"),
        ("한글", "한글"),
        ("Ελλάδα", "Ελλαδα"),
        # Letters without a decomposition pass through unchanged.
        ("øß", "øß"),
        # NFKD also folds compatibility characters such as ligatures.
        ("ﬁre", "fire"),
    ],
)
def test_strip_accents(string: str, expected: str) -> None:
    """Should strip accents from a string while preserving non-Latin scripts."""
    assert strip_accents(string) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("plain text", "plain text"),
        ("", ""),
        # HTML tags.
        ("<b>bold</b>", "bold"),
        ("<i>italic</i>", "italic"),
        ("<span style='font-weight:bold'>hello</span>", "hello"),
        ("<p>hello <strong>world</strong></p>", "hello world"),
        ("<br/>line<br/>", "line"),
        # HTML entities.
        ("Tom &amp; Jerry", "Tom & Jerry"),
        ("&lt;tag&gt;", "<tag>"),
        ("caf&eacute;", "café"),
        # Unicode-styled characters from Mathematical Alphanumeric Symbols.
        ("𝐛𝐨𝐥𝐝", "bold"),
        ("𝑖𝑡𝑎𝑙𝑖𝑐", "italic"),
        ("𝓯𝓪𝓷𝓬𝔂", "fancy"),
        ("𝔅𝔩𝔞𝔠𝔨", "Black"),
        ("𝙼𝙾𝙽𝙾", "MONO"),
        ("𝔸ℂ𝔻", "ACD"),
        ("𝟏𝟐𝟑", "123"),
        # Ligatures and full-width forms.
        ("ﬁre", "fire"),
        ("Ｈｅｌｌｏ", "Hello"),
        # Diacritics are preserved.
        ("café", "café"),
        ("Héllo Wörld", "Héllo Wörld"),
        # Combined: HTML wrapping styled unicode.
        ("<b>𝐡𝐞𝐥𝐥𝐨</b> &amp; <i>𝑤𝑜𝑟𝑙𝑑</i>", "hello & world"),
        # Zero-width and bidi formatting characters are removed.
        ("hel\u200blo", "hello"),
        ("a\u200db\ufeffc", "abc"),
    ],
)
def test_strip_styling(string: str, expected: str) -> None:
    """Should strip styling from text."""
    assert strip_styling(string) == expected

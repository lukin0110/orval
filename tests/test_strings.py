"""Tests for the string manipulation functions."""

import pytest
from typeguard import suppress_type_checks

from orval import (
    camel_case,
    dot_case,
    fence,
    has_control,
    kebab_case,
    mask,
    pascal_case,
    slugify,
    snake_case,
    squish,
    strip_accents,
    strip_control,
    strip_styling,
    train_case,
    truncate,
    truncate_bytes,
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
        ("hello world", 8, "...", "hello..."),
        ("hello world", 5, "...", "he..."),
        ("hello world", 4, "...", "h..."),
        ("hello world", 5, "--", "hel--"),
        ("hello world", 11, "...", "hello world"),
        ("hello world", 12, "...", "hello world"),
        ("hello", 5, "...", "hello"),
        ("hello", 4, "...", "h..."),
        ("hello world", 5, "", "hello"),
        ("abcdef", 3, "", "abc"),
        ("a", 1, "", "a"),
        ("", 5, "...", ""),
    ],
)
def test_truncate(string: str, number: int, suffix: str, expected: str) -> None:
    """Should truncate a string to at most a certain number of characters."""
    assert truncate(string, number, suffix) == expected


def test_truncate_invalid() -> None:
    """Should raise a ValueError for a non-positive 'number' or an oversized 'suffix'."""
    with pytest.raises(ValueError, match=r"Number must be a positive integer."):
        truncate("hello world", 0)
    with pytest.raises(ValueError, match=r"Number must be a positive integer."):
        truncate("hello world", -1)
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of characters."):
        truncate("hello world", 3)
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of characters."):
        truncate("hello world", 2)
    # The check depends only on the arguments, not on whether the input would need cutting.
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of characters."):
        truncate("a", 2)


def test_truncate_respects_limit() -> None:
    """Should never return more than 'number' characters, whatever the suffix."""
    string = "abcdefghijkl"
    for suffix in ("", ".", "...", " [more]"):
        for number in range(len(suffix) + 1, 15):
            result = truncate(string, number, suffix)
            assert len(result) <= number
            if len(string) > number:
                assert len(result) == number
                assert result.endswith(suffix)
                assert string.startswith(result[: number - len(suffix)])
            else:
                assert result == string


@pytest.mark.parametrize(
    ("string", "max_bytes", "suffix", "expected"),
    [
        # ASCII encodes one byte per character, so the byte budget is the character budget.
        ("hello world", 8, "", "hello wo"),
        ("hello world", 8, "...", "hello..."),
        ("hello world", 11, "...", "hello world"),
        ("hello world", 12, "...", "hello world"),
        ("", 5, "...", ""),
        # 'héllo wörld' encodes to 13 bytes: 'é' and 'ö' take two each.
        ("héllo wörld", 8, "", "héllo w"),
        # Byte 9 would split 'ö', so the whole character is dropped and a byte goes unused.
        ("héllo wörld", 9, "", "héllo w"),
        ("héllo wörld", 10, "", "héllo wö"),
        ("héllo wörld", 13, "", "héllo wörld"),
        # Three bytes per character: a cut can leave one or two bytes unused.
        ("日本語", 7, "", "日本"),
        ("日本語", 8, "", "日本"),
        ("日本語", 9, "", "日本語"),
        # An emoji takes four bytes and is never split, however close the budget comes.
        ("a💩b", 4, "", "a"),
        ("a💩b", 5, "", "a💩"),
        ("a💩b", 6, "", "a💩b"),
        # The suffix is encoded too: '…' spends three of the available bytes.
        ("日本語", 7, "…", "日…"),
        ("hello world", 8, "…", "hello…"),
    ],
)
def test_truncate_bytes(string: str, max_bytes: int, suffix: str, expected: str) -> None:
    """Should truncate a string to at most a certain number of UTF-8 bytes."""
    assert truncate_bytes(string, max_bytes, suffix) == expected


def test_truncate_bytes_invalid() -> None:
    """Should raise a ValueError for a non-positive 'max_bytes' or an oversized 'suffix'."""
    with pytest.raises(ValueError, match=r"Max bytes must be a positive integer."):
        truncate_bytes("hello world", 0)
    with pytest.raises(ValueError, match=r"Max bytes must be a positive integer."):
        truncate_bytes("hello world", -1)
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of bytes."):
        truncate_bytes("hello world", 3, "...")
    # The suffix is measured in bytes, not characters: a one-character '…' takes three of them,
    # which a three-byte budget cannot spare.
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of bytes."):
        truncate_bytes("hello world", 3, "…")
    # The check depends only on the arguments, not on whether the input would need cutting.
    with pytest.raises(ValueError, match=r"Suffix must be shorter than the number of bytes."):
        truncate_bytes("a", 2, "...")


@pytest.mark.parametrize("suffix", ["", ".", "...", "…"])
def test_truncate_bytes_respects_limit(suffix: str) -> None:
    """Should never exceed 'max_bytes', and never cut a character in half."""
    string = "aé日\U0001f600büz"
    encoded_length = len(string.encode("utf-8"))
    for max_bytes in range(len(suffix.encode("utf-8")) + 1, encoded_length + 4):
        result = truncate_bytes(string, max_bytes, suffix)
        assert len(result.encode("utf-8")) <= max_bytes
        if encoded_length <= max_bytes:
            assert result == string
        else:
            assert result.endswith(suffix)
            # A prefix of the original can only survive the round trip if no character was
            # split: a partial sequence would have decoded to a replacement or been dropped.
            cut = result[: len(result) - len(suffix)] if suffix else result
            assert string.startswith(cut)


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


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("plain text", "plain text"),
        ("", ""),
        # Newline, carriage return and tab.
        ("user\nname", "username"),
        ("a\r\nb", "ab"),
        ("col\tumn", "column"),
        # NUL and other low controls.
        ("id\x00", "id"),
        ("\x01\x02abc\x1f", "abc"),
        # Escape is removed; the printable tail of an ANSI sequence stays.
        ("\x1b[31mred\x1b[0m", "[31mred[0m"),
        # DEL.
        ("del\x7f", "del"),
        # Neighbours of the range are untouched: space, tilde and C1 controls.
        (" \x20!", "  !"),
        ("~\x7e", "~~"),
        ("\x80\x9f", "\x80\x9f"),
        # Non-ASCII and zero-width characters are untouched (see 'strip_styling').
        ("café こんにちは", "café こんにちは"),
        ("hel\u200blo", "hel\u200blo"),
    ],
)
def test_strip_control(string: str, expected: str) -> None:
    """Should strip ASCII control characters from a string."""
    assert strip_control(string) == expected


@pytest.mark.parametrize(
    ("string", "replacement", "expected"),
    [
        ("user\nname", " ", "user name"),
        # One replacement per control character, no collapsing.
        ("a\r\nb", " ", "a  b"),
        ("a\x00b\x7fc", "?", "a?b?c"),
        # Multi-character replacement, and backslashes are taken literally (no re.sub
        # template expansion).
        ("tab\there", "\\t", "tab\\there"),
        ("a\x00b", "\\", "a\\b"),
        ("a\x00b", "\\1", "a\\1b"),
        ("clean", "?", "clean"),
        ("", "?", ""),
    ],
)
def test_strip_control_replacement(string: str, replacement: str, expected: str) -> None:
    """Should replace each ASCII control character with the given replacement."""
    assert strip_control(string, replacement=replacement) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("plain text", False),
        ("", False),
        # Newline, carriage return and tab.
        ("user\nname", True),
        ("a\r\nb", True),
        ("col\tumn", True),
        # NUL and other low controls.
        ("id\x00", True),
        ("\x01\x02abc\x1f", True),
        # Escape; the printable tail of an ANSI sequence on its own does not count.
        ("\x1b[31mred\x1b[0m", True),
        ("[31mred[0m", False),
        # DEL.
        ("del\x7f", True),
        # Neighbours of the range are not control characters: space, tilde and C1 controls.
        (" \x20!", False),
        ("~\x7e", False),
        ("\x80\x9f", False),
        # Non-ASCII and zero-width characters are not control characters.
        ("café こんにちは", False),
        ("hel\u200blo", False),
    ],
)
def test_has_control(string: str, expected: bool) -> None:
    """Should report whether a string contains an ASCII control character."""
    assert has_control(string) is expected


@pytest.mark.parametrize(
    "string",
    [
        "plain text",
        "",
        "user\nname",
        "\x1b[31mred\x1b[0m",
        "del\x7f",
        "hel\u200blo",
    ],
)
def test_has_control_matches_strip_control(string: str) -> None:
    """Should agree with 'strip_control' about which strings contain control characters."""
    assert has_control(string) is (strip_control(string) != string)


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("hello world", "hello world"),
        ("", ""),
        ("   ", ""),
        # Both ends are stripped.
        ("  hello  ", "hello"),
        ("\n\thello\n", "hello"),
        # Interior runs collapse to a single space, whatever they are made of.
        ("a    b", "a b"),
        ("a\tb", "a b"),
        ("hello\nworld", "hello world"),
        ("a \t\n\r b", "a b"),
        ("  Great   Scott  ", "Great Scott"),
        # Unicode whitespace counts too: non-breaking space and en quad.
        ("a\xa0b", "a b"),
        ("a\u2000b", "a b"),
        ("\xa0hello\xa0", "hello"),
        # Punctuation, case, accents and non-Latin scripts are left untouched.
        ("Great,  Scott!", "Great, Scott!"),
        ("Héllo   Wörld", "Héllo Wörld"),
        ("café   こんにちは", "café こんにちは"),
        # Zero-width characters are not whitespace (see 'strip_styling').
        ("hel\u200blo", "hel\u200blo"),
    ],
)
def test_squish(string: str, expected: str) -> None:
    """Should collapse whitespace runs to a single space and strip both ends."""
    assert squish(string) == expected


@pytest.mark.parametrize(
    "string",
    [
        "hello world",
        "",
        "   ",
        "  Great   Scott  ",
        "a \t\n\r b",
        "a\xa0b",
        "hel\u200blo",
    ],
)
def test_squish_is_idempotent(string: str) -> None:
    """Should leave an already squished string unchanged."""
    assert squish(squish(string)) == squish(string)


@pytest.mark.parametrize(
    ("content", "char", "minimum", "expected"),
    [
        # Nothing to escape: the minimum is returned as is.
        ("", "`", 3, "```"),
        ("no fences here", "`", 3, "```"),
        # Runs shorter than the minimum do not matter either.
        ("inline `code` span", "`", 3, "```"),
        ("a `` b", "`", 3, "```"),
        # A fence inside the content pushes the result one longer.
        ("```python\nprint()\n```", "`", 3, "````"),
        # The longest run wins, wherever it sits.
        ("````\n```\n", "`", 3, "`````"),
        ("x ``````` y", "`", 3, "````````"),
        # Runs are counted anywhere, not only at the start of a line.
        ("a ``` b", "`", 3, "````"),
        # Only the fence character counts.
        ("~~~", "`", 3, "```"),
        ("```", "~", 3, "~~~"),
        ("~~~", "~", 3, "~~~~"),
        # A single backtick is a valid inline code span delimiter.
        ("a", "`", 1, "`"),
        ("`", "`", 1, "``"),
        ("a `` b", "`", 1, "```"),
        # The minimum dominates a short run.
        ("``", "`", 5, "`````"),
        ("`````", "`", 5, "``````"),
        # A regex metacharacter works as the fence character too.
        ("a ** b", "*", 3, "***"),
        ("a *** b", "*", 3, "****"),
    ],
)
def test_fence(content: str, char: str, minimum: int, expected: str) -> None:
    """Should return the shortest fence, at least 'minimum' long, that 'content' cannot close."""
    assert fence(content, char=char, minimum=minimum) == expected


def test_fence_invalid() -> None:
    """Should raise a ValueError for a 'char' that is not one character or a non-positive 'minimum'."""
    with pytest.raises(ValueError, match=r"Char must be a single character."):
        fence("hello", char="")
    with pytest.raises(ValueError, match=r"Char must be a single character."):
        fence("hello", char="``")
    with pytest.raises(ValueError, match=r"Minimum must be a positive integer."):
        fence("hello", minimum=0)
    with pytest.raises(ValueError, match=r"Minimum must be a positive integer."):
        fence("hello", minimum=-1)


@pytest.mark.parametrize(
    "content",
    [
        "",
        "plain text",
        "a ``` b",
        "````\n```",
        "` `` ``` ````",
        "```python\nprint('`')\n```\n",
        "*+?[](){}|^$.\\ ``` *+?",
    ],
)
def test_fence_cannot_be_closed(content: str) -> None:
    """Should return the shortest run of at least 'minimum' backticks that does not occur in 'content'."""
    for minimum in range(1, 6):
        result = fence(content, minimum=minimum)
        assert set(result) == {"`"}
        assert len(result) >= minimum
        assert result not in content
        # Shortest: either the minimum was enough, or one backtick fewer would have been closable.
        assert len(result) == minimum or result[:-1] in content

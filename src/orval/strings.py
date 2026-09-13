"""String utilities.

More info on casing naming conventions:
https://en.wikipedia.org/wiki/Naming_convention_(programming)
"""

import html
import re
import unicodedata

_HTML_TAG_RE = re.compile(r"<[^<>]+>")
# Zero-width and bidi-formatting characters that often hitchhike with copy/pasted text.
# Covers: ZWSP/ZWNJ/ZWJ + LRM/RLM (U+200B-U+200F), bidi embedding/override controls
# (U+202A-U+202E), word joiner / invisible operators (U+2060-U+206F), and BOM (U+FEFF).
_ZERO_WIDTH_RE = re.compile("[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff]")  # ruff: ignore[unraw-re-pattern]
# ASCII control characters: C0 controls (NUL..US, incl. tab/newline/escape) and DEL.
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
# Which end of the string stays visible when masking: leading or trailing characters.
_SIDES: set[str] = {"l", "r"}


def _normalize(string: str, unicode: bool = True, compact_spaces: bool = True) -> str:
    """Normalize a string for casing.

    Replace non-alphanumeric characters (except whitespace) with spaces. Leading and trailing whitespace will be stripped.

    - If 'unicode' is True, unicode characters will be preserved.
    - If 'unicode' is False unicode characters will be by ASCII characters.
    - If unicode characters can't be replaced the will be replaced by a space.
    - If 'compact_spaces' is True, multiple consecutive spaces will be reduced to a single space.

    Parameters
    ----------
    string
        The input string to be normalized.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).
    compact_spaces
        If True, multiple consecutive spaces are reduced to a single space (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    if unicode:
        # Normalize the string to Normalization Form Compatibility Composition (NFKC).
        # This will replace multiple representation by a normalized one. E.g. 'ö' can have two representations.
        value = unicodedata.normalize("NFKC", string)
        text = re.sub(r"[^\w\s]|_", " ", value, flags=re.UNICODE)
    else:
        # Normalize the string to Normalization Form Compatibility Decomposition (NFKD).
        # This will replace the diacritics by ASCII characters. E.g. 'ö' will be replaced by 'o' and 'ì' by 'i'.
        value = unicodedata.normalize("NFKD", string).encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^\w\s]|_", " ", value)

    # Replace multiple spaces with a single space
    return re.sub(r"\s+", " ", text).strip() if compact_spaces else text.strip()


def kebab_case(string: str, scream: bool = False, unicode: bool = True, compact_spaces: bool = True) -> str:
    """Convert a string to kebab-case.

    Parameters
    ----------
    string
        Input string to transform.
    scream
        Convert the output to uppercase.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).
    compact_spaces
        If True, multiple consecutive spaces are reduced to a single space (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    text = _normalize(string, unicode=unicode, compact_spaces=compact_spaces).replace(" ", "-")
    return text.lower() if not scream else text.upper()


def slugify(string: str) -> str:
    """Create a slug from a given string.

    Normalize strings to a 'slug'. Can be used to format URL's or resource names (eg: Database name). If you want more
     flexibility, you can use 'kebab_case'.

    Parameters
    ----------
    string
        Input string to transform.

    Returns
    -------
    str
        Returns a transformed string.
    """
    return kebab_case(string, unicode=False, compact_spaces=True)


def _dromedary_case(string: str, upper: bool = False, join_char: str = "", unicode: bool = True) -> str:
    """Convert a string to dromedaryCase/DromedaryCase.

    Can be used for camelCase, UpperCamelCase, and PascalCase. PascalCase and UpperCamelCase are
    interchangeable. PascalCase originates from Pascal programming language, which popularized this
    style.
    """
    words = _normalize(string, unicode=unicode, compact_spaces=True).split(" ")
    camel_case_words = [words[0].lower() if not upper else words[0].capitalize()] + [
        word.capitalize() for word in words[1:]
    ]
    return join_char.join(camel_case_words)


def camel_case(string: str, unicode: bool = True) -> str:
    """Convert a string to camelCase.

    Parameters
    ----------
    string
        Input string to transform.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=False, unicode=unicode)


def pascal_case(string: str, unicode: bool = True) -> str:
    """Convert a string to PascalCase.

    Parameters
    ----------
    string
        Input string to transform.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=True, unicode=unicode)


def train_case(string: str, unicode: bool = False) -> str:
    """Convert a string to train-case.

    Also known as HTTP-Header-Case, this style is used for HTTP headers. For HTTP headers it is recommended to use
    ASCII characters since all parties need to be aligned (sender, receiver, and intermediaries). Hence, 'unicode' is
    False by default.

    Parameters
    ----------
    string
        Input string to transform.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is False).

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=True, join_char="-", unicode=unicode)


def snake_case(string: str, scream: bool = False, unicode: bool = True, compact_spaces: bool = True) -> str:
    """Convert a string to snake_case.

    Parameters
    ----------
    string
        Input string to transform.
    scream
        Convert the output to uppercase.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).
    compact_spaces
        If True, multiple consecutive spaces are reduced to a single space (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    text = _normalize(string, unicode=unicode, compact_spaces=compact_spaces).replace(" ", "_")
    return text.lower() if not scream else text.upper()


def dot_case(string: str, scream: bool = False, unicode: bool = True, compact_spaces: bool = True) -> str:
    """Convert a string to dot.case.

    Parameters
    ----------
    string
        Input string to transform.
    scream
        Convert the output to uppercase.
    unicode
        If True, allows Unicode characters in the output string. If False, only ASCII characters are allowed (default is True).
    compact_spaces
        If True, multiple consecutive spaces are reduced to a single space (default is True).

    Returns
    -------
    str
        Returns a transformed string.
    """
    text = _normalize(string, unicode=unicode, compact_spaces=compact_spaces).replace(" ", ".")
    return text.lower() if not scream else text.upper()


def truncate(string: str, number: int, /, suffix: str = "...") -> str:
    """Truncate a string to at most a certain number of characters.

    If the string already fits it is returned unchanged. Otherwise it is cut so that
    the result, including the suffix, is exactly 'number' characters long. Pass an
    empty suffix for a plain cut.

    Parameters
    ----------
    string
        The string to truncate.
    number
        The maximum number of characters the result may contain.
    suffix
        Appended to the cut string to signal truncation (default is "...").
        Counts toward 'number'.

    Returns
    -------
    str
        The string, or its prefix plus the suffix, never longer than 'number'.

    Raises
    ------
    ValueError
        If 'number' is not a positive integer, or if 'suffix' is not shorter
        than 'number'.

    Examples
    --------
    >>> truncate("hello world", 8)
    'hello...'
    >>> truncate("hello world", 8, suffix="")
    'hello wo'
    >>> truncate("hello", 8)
    'hello'
    """
    if number <= 0:
        raise ValueError("Number must be a positive integer.")
    if len(suffix) >= number:
        raise ValueError("Suffix must be shorter than the number of characters.")
    if len(string) <= number:
        return string
    return f"{string[: number - len(suffix)]}{suffix}"


def truncate_bytes(string: str, max_bytes: int, /, suffix: str = "") -> str:
    """Truncate so that the UTF-8 encoding is at most 'max_bytes', never mid-character.

    Where 'truncate' counts characters, this counts the bytes of the UTF-8 encoding, the
    limit that protocols and storage actually impose: the 75-octet line length of an iCalendar
    (RFC 5545) fold, the 4096-byte cap on a web push payload, a ``VARCHAR`` column whose length
    is measured in bytes. Cutting the encoded form directly can land inside a multi-byte
    sequence and produce invalid UTF-8; this backs the cut up to the nearest character boundary
    instead, dropping the partial character whole.

    If the string already fits it is returned unchanged. Because characters vary in width, a
    truncated result is at most 'max_bytes' rather than exactly 'max_bytes': backing off a
    boundary can leave up to three bytes unused.

    A string holding a lone surrogate has no UTF-8 encoding, so 'UnicodeEncodeError'
    propagates from the encode step. Truncation is per character, not per grapheme cluster: a
    combining accent can be separated from the letter it modifies, and an emoji joined by
    zero-width joiners can be cut between its parts.

    Parameters
    ----------
    string
        The string to truncate.
    max_bytes
        The maximum number of bytes the UTF-8 encoding of the result may occupy.
    suffix
        Appended to the cut string to signal truncation (default is ""). Its own encoded
        length counts toward 'max_bytes'.

    Returns
    -------
    str
        The string, or a prefix of it plus the suffix, encoding to at most 'max_bytes' bytes.

    Raises
    ------
    ValueError
        If 'max_bytes' is not a positive integer, or if the encoded 'suffix' is not shorter
        than 'max_bytes'.

    Examples
    --------
    >>> truncate_bytes("héllo wörld", 9)
    'héllo w'
    >>> truncate_bytes("日本語", 7)
    '日本'
    >>> truncate_bytes("日本語", 7, suffix="…")
    '日…'
    >>> truncate_bytes("hello", 8)
    'hello'
    """
    if max_bytes <= 0:
        raise ValueError("Max bytes must be a positive integer.")
    suffix_bytes = len(suffix.encode("utf-8"))
    if suffix_bytes >= max_bytes:
        raise ValueError("Suffix must be shorter than the number of bytes.")
    encoded = string.encode("utf-8")
    if len(encoded) <= max_bytes:
        return string
    # Slicing the encoded bytes can land inside a multi-byte sequence, which is exactly what
    # "ignore" discards: it already knows where the character boundaries are, so there is no
    # need to scan back over continuation bytes by hand. Nothing else can be dropped, because
    # the bytes came from a str and the cut tail is the only part that can be invalid.
    return f"{encoded[: max_bytes - suffix_bytes].decode('utf-8', 'ignore')}{suffix}"


def mask(string: str, /, show: int = 4, side: str = "r", mask_char: str = "*") -> str:
    """Mask a string, keeping a few characters visible.

    Useful for redacting sensitive values (API keys, tokens, card numbers) while
    keeping enough characters visible to identify them. The output has the same
    length as the input. When 'show' is greater than or equal to the length of the
    string, every character is masked so that a short secret is never revealed.

    Parameters
    ----------
    string
        The string to mask.
    show
        Number of characters to leave visible (default is 4).
    side
        Which end stays visible. One of "l" (leading), "r" (trailing).
        Default is "r".
    mask_char
        The character used for masking (default is "*").

    Returns
    -------
    str
        The masked string, e.g. ``"********3xyz"``.

    Raises
    ------
    ValueError
        If 'show' is negative, 'side' is not recognized, or 'mask_char' is not a
        single character.
    """
    if not isinstance(string, str):
        raise TypeError("Value must be a string.")
    if show < 0:
        raise ValueError("Show must be a non-negative integer.")
    if side not in _SIDES:
        raise ValueError(f"Side must be one of {_SIDES}.")
    if len(mask_char) != 1:
        raise ValueError("Mask char must be a single character.")
    if show >= len(string):
        return mask_char * len(string)
    hidden = mask_char * (len(string) - show)
    return string[:show] + hidden if side == "l" else hidden + string[len(string) - show :]


def strip_accents(string: str) -> str:
    """Strip accents (diacritical marks) from a string.

    Decomposes characters (NFKD), removes combining marks, and recomposes (NFC).
    E.g. 'café' becomes 'cafe' and 'Héllo Wörld' becomes 'Hello World'. Unlike
    'slugify', non-Latin scripts are preserved: 'こんにちは' stays 'こんにちは'.
    Letters without a decomposition (e.g. 'ø', 'ß') are left unchanged.

    Parameters
    ----------
    string
        Input string to strip accents from.

    Returns
    -------
    str
        The string with diacritical marks removed.
    """
    decomposed = unicodedata.normalize("NFKD", string)
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    return unicodedata.normalize("NFC", stripped)


def strip_styling(string: str) -> str:
    """Strip styling from text to obtain plain text.

    Useful when text gets copy/pasted into an HTML input field from a styled
    source (e.g., word processor, social media, rich text editor). It:

    - Removes HTML tags (e.g., ``<b>``, ``<i>``, ``<span style="...">``).
    - Decodes HTML entities (e.g., ``&amp;`` → ``&``, ``&lt;`` → ``<``).
    - Normalizes Unicode 'styled' characters from the Mathematical Alphanumeric
      Symbols block (bold, italic, script, fraktur, double-struck, monospace,
      etc.) to their plain equivalents.
    - Collapses ligatures and full-width forms (e.g., ``ﬁ`` → ``fi``, ``Ａ`` → ``A``).
    - Normalizes other Unicode compatibility forms via NFKC (e.g., circled
      numbers ``①`` → ``1``, Roman numerals ``Ⅷ`` → ``VIII``, superscripts
      ``²`` → ``2``, fractions ``½`` → ``1/2``).
    - Removes zero-width and bidi-formatting characters.

    Diacritics and non-ASCII letters are preserved (e.g., ``café`` stays ``café``).

    Parameters
    ----------
    string
        Input string to strip styling from.

    Returns
    -------
    str
        Returns the plain text version of the input.
    """
    without_tags = _HTML_TAG_RE.sub("", string)
    decoded = html.unescape(without_tags)
    normalized = unicodedata.normalize("NFKC", decoded)
    return _ZERO_WIDTH_RE.sub("", normalized)


def strip_control(string: str, replacement: str = "") -> str:
    """Strip ASCII control characters from a string.

    Removes (or replaces) the C0 control characters ``U+0000``–``U+001F``
    (including tab, newline, carriage return and escape) and DEL (``U+007F``).
    Useful before writing untrusted values into a log line or terminal, where a
    stray newline would split one record into two or forge an extra line.

    Each control character is replaced individually, so a carriage return
    followed by a newline with ``replacement=" "`` becomes two spaces. Only the
    control character itself is removed: the printable tail of an ANSI escape
    sequence (e.g. ``[31m`` after the escape character) is left in place.
    Non-ASCII text, zero-width characters and C1 controls (``U+0080``–``U+009F``)
    are untouched; see ``strip_styling`` for zero-width characters.

    Parameters
    ----------
    string
        Input string to strip control characters from.
    replacement
        String to substitute, literally, for each control character. Defaults to ``""``.

    Returns
    -------
    str
        The string with control characters removed or replaced.
    """
    # A callable makes re.sub use the replacement literally; as a string it would be
    # expanded as a template, so a backslash in the replacement would break or mangle it.
    return _CONTROL_RE.sub(lambda _: replacement, string)


def has_control(string: str) -> bool:
    """Check whether a string contains an ASCII control character.

    The predicate behind ``strip_control``: it recognizes exactly the same
    characters, the C0 controls ``U+0000``-``U+001F`` (including tab, newline,
    carriage return and escape) and DEL (``U+007F``). Non-ASCII text, zero-width
    characters and C1 controls (``U+0080``-``U+009F``) do not count, and neither
    does the printable tail of an ANSI escape sequence (e.g. ``[31m``).

    Use it where a control character is a reason to reject a value rather than
    repair it, such as a path component or an identifier, where a sanitized
    string would silently name something else. It answers that question without
    building a scrubbed copy only to compare it away.

    Parameters
    ----------
    string
        Input string to check for control characters.

    Returns
    -------
    bool
        True if the string contains at least one ASCII control character, False otherwise.
    """
    return bool(_CONTROL_RE.search(string))

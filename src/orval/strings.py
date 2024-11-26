"""String utilities.

More info on casing naming conventions:
https://en.wikipedia.org/wiki/Naming_convention_(programming)
"""

import re
import unicodedata


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


def truncate(string: str, number: int, /, suffix: str = "...") -> str:
    """Truncate a string to a certain number of characters."""
    if number <= 0:
        raise ValueError("Number must be a positive integer.")
    if len(string) <= number:
        return string
    return f"{string[: number - 1]}{suffix}"

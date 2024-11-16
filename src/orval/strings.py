"""String utilities.

More info on casing naming conventions:
https://en.wikipedia.org/wiki/Naming_convention_(programming)
"""

import re
import unicodedata


def slugify(string: str, allow_unicode: bool = False) -> str:
    """Create a slug from a given string.

    Normalize strings to a 'slug'. Can be used to format URL's or resource names (eg: Database name).

    Convert to ASCII if 'allow_unicode' is False.
    Convert any single or consecutive spaces, dots or hyphens to a single hyphen.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase.
    Strip leading and trailing whitespace.

    Parameters
    ----------
    string
        Input string to transform.
    allow_unicode
        The output may contain unicode characters.

    Returns
    -------
    str
        Returns a transformed string.
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", string)
    else:
        value = unicodedata.normalize("NFKD", string).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s\-.]", "", value).strip().lower()
    return re.sub(r"[\s\-.]+", "-", value)


def _normalize(string: str) -> str:
    """Normalize a string for casing.

    Replace non-alphanumeric characters (except whitespace) with spaces but preserve diacritic
    characters like ö, ì, etc.
    """
    text = re.sub(r"[^\w\s]", " ", string, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _dromedary_case(string: str, upper: bool = False, join_char: str = "") -> str:
    """Convert a string to dromedaryCase/DromedaryCase.

    Can be used for camelCase, UpperCamelCase, and PascalCase. PascalCase and UpperCamelCase are
    interchangeable. PascalCase originates from Pascal programming language, which popularized this
    style.
    """
    words = _normalize(string).split(" ")
    camel_case_words = [words[0].lower() if not upper else words[0].capitalize()] + [
        word.capitalize() for word in words[1:]
    ]
    return join_char.join(camel_case_words)


def camel_case(string: str) -> str:
    """Convert a string to camelCase.

    Parameters
    ----------
    string
        Input string to transform.

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=False)


def pascal_case(string: str) -> str:
    """Convert a string to PascalCase.

    Parameters
    ----------
    string
        Input string to transform.

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=True)


def train_case(string: str) -> str:
    """Convert a string to train-case.

    Also known as HTTP-Header-Case, this style is used for HTTP headers.

    Parameters
    ----------
    string
        Input string to transform.

    Returns
    -------
    str
        Returns a transformed string.
    """
    return _dromedary_case(string, upper=True, join_char="-")


def kebab_case(string: str, scream: bool = False) -> str:
    """Convert a string to kebab-case.

    Parameters
    ----------
    string
        Input string to transform.
    scream
        Convert the output to uppercase.

    Returns
    -------
    str
        Returns a transformed string.
    """
    text = _normalize(string).replace(" ", "-")
    return text.lower() if not scream else text.upper()


def snake_case(string: str, scream: bool = False) -> str:
    """Convert a string to snake_case.

    Parameters
    ----------
    string
        Input string to transform.
    scream
        Convert the output to uppercase.

    Returns
    -------
    str
        Returns a transformed string.
    """
    text = re.sub(r"\s+", " ", _normalize(string)).replace(" ", "_")
    return text.lower() if not scream else text.upper()


def truncate(string: str, number: int, /, suffix: str = "...") -> str:
    """Truncate a string to a certain number of characters."""
    if number <= 0:
        raise ValueError("Number must be a positive integer.")
    if len(string) <= number:
        return string
    return f"{string[: number - 1]}{suffix}"

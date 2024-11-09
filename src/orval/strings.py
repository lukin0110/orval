"""String utilities."""

import re
import unicodedata


def slugify(value: str, allow_unicode: bool = False) -> str:
    """Create a slug from a given string.

    Normalize strings to a 'slug'. Can be used to format URL's or resource names (eg: Database name).

    Convert to ASCII if 'allow_unicode' is False.
    Convert any single or consecutive spaces, dots or hyphens to a single hyphen.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase.
    Strip leading and trailing whitespace.

    Parameters
    ----------
    value
        Input string to transform.
    allow_unicode
        The output may contain unicode characters.

    Returns
    -------
    str
        Returns a transformed string.
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s\-.]", "", value).strip().lower()
    return re.sub(r"[\s\-.]+", "-", value)


def camel_case(string: str) -> str:
    """Convert a string to camelCase."""
    input_ = string.strip()
    words = input_.split(" ")
    camel_case_words = [words[0].lower()] + [word.capitalize() for word in words[1:]]
    return "".join(camel_case_words)


def kebab_case(string: str) -> str:
    """Convert a string to kebab-case."""
    input_ = string.strip().lower()
    return input_.replace(" ", "-")


def pascal_case(string: str) -> str:
    """Convert a string to PascalCase."""
    words = string.split()
    return "".join(word.capitalize() for word in words)


def snake_case(string: str) -> str:
    """Convert a string to snake_case."""
    input_ = string.strip().lower()
    return input_.replace(" ", "_")

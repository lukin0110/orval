"""."""

import pytest

from orval import camel_case, kebab_case, pascal_case, snake_case, train_case, truncate


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
    assert train_case(string) == expected


@pytest.mark.parametrize(
    ("string", "scream", "expected"),
    [
        ("great scott", False, "great-scott"),
        ("Great Scott", False, "great-scott"),
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
    ],
)
def test_kebab_case(string: str, scream: bool, expected: str) -> None:
    """Should convert a string to kebab-case."""
    assert kebab_case(string, scream) == expected


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
        with pytest.raises(ValueError, match="Number must be a positive integer."):
            truncate(string, number, suffix)
    else:
        assert truncate(string, number, suffix) == expected

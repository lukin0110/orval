"""Tests hashify function."""

from decimal import Decimal
from itertools import product
from typing import Any

import pytest

from orval.hashing import hashify

GUARANTEED_ALGORITHMS = {
    "sha3_256": 64,
    "sha512": 128,
    "blake2s": 64,
    "sha3_224": 56,
    "sha3_384": 96,
    "sha224": 56,
    "sha256": 64,
    "sha3_512": 128,
    "blake2b": 128,
    "sha1": 40,
    "sha384": 96,
    "md5": 32,
    "shake_128": 128,
    "shake_256": 128,
}
GUARANTEED_LENGTHS = list(GUARANTEED_ALGORITHMS.items())
GUARANTEED_PRODUCT = [(x, y) for x, y in product(GUARANTEED_ALGORITHMS.keys(), GUARANTEED_ALGORITHMS.keys()) if x != y]


@pytest.mark.parametrize(("alg", "length"), GUARANTEED_LENGTHS)
def test__algorithms__success(alg: str, length: int) -> None:
    """Should return a hexadecimal string representing any python object."""
    values = ["great scott", "", None, 1, 1.1, Decimal("1.1"), {"g": "s"}, {1, 2}, [1, 2], object()]
    for value in values:
        result = hashify(value, alg)
        assert isinstance(result, str)
        assert len(result) == length, f"type={type(value)}"


@pytest.mark.parametrize(("alg_1", "alg_2"), GUARANTEED_PRODUCT)
def test__different_algorithms__success(alg_1: str, alg_2: str) -> None:
    """Should return different hashes for different algorithms."""
    obj = "test_string"
    result_sha256 = hashify(obj, alg=alg_1)
    result_md5 = hashify(obj, alg=alg_2)
    assert result_sha256 != result_md5


def test___unsupported_algorithm__fairure() -> None:
    """Should raise a ValueError for an unsupported algorithm."""
    with pytest.raises(ValueError, match="Hashing algorithm 'unsupported_alg' not supported."):
        hashify("", alg="unsupported_alg")


@pytest.mark.parametrize(
    ("alg", "obj", "expected"),
    [
        ("md5", "great", "acaa16770db76c1ffb9cee51c3cabfcf"),
        (
            "md5",
            [],
            "d34b2ff3ebd47dff1d21eee2d69d4ffd",
        ),
        ("sha256", "scott", "12a303c224c250d07c81691de6e0fd74699ce6bd78c234057de70413a58457cf"),
        ("sha256", 1, "4d672a9db795f0105d536626cd190c28ed199cc8d145e2349e5457f7ff6f38be"),
        ("sha256", set(), "0cdaff94fb5e168a49c2a0b2807ed3972fce8e480f1250e43ec781d150f077ec"),
        ("sha256", object(), "73f109a46d7d1ba94c6ce0997ab29937fcc86e2ec93468b76c7ac8cfa0919638"),
        ("sha256", None, "4f3fc348a818941a464e415fff6b9d416c1ddc3b1c64743861d328fbc345bcd6"),
        (
            "sha512",
            "jigowatt",
            "80dba8b5dabe06e380343603c235c2e29ca99f3dade9c6d6e603c75e833a4b960329a019b443a04cd8360d972326c4b9c0470944641c733131ee704421be7e86",
        ),
        (
            "sha512",
            {},
            "06d4f7503aef23b72dc00355f83eb77d9ff0fee3216251c91b63aa071cc3d234ed0d76d527a277cf9a51a77fa946a08ddfde02de8cd12e6e1362330d1e1dca3e",
        ),
    ],
)
def test__sanity_checks__success(alg: str, obj: Any, expected: str) -> None:
    """Should return expected values.

    A simple and basic sanity check to ensure that the function is generating consistent hashes.

    Is there a better approach to do sanity checks without listing a huge table of parameterized values?
    """
    assert hashify(obj, alg=alg) == expected, f"{alg}={type(obj)}"

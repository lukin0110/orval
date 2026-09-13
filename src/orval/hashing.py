"""Cryptographic hash for any Python object."""

import hashlib
import pickle  # ruff: ignore[suspicious-pickle-import]
from typing import Any


def hashify(obj: Any, alg: str = "sha256") -> str:
    """Compute a hash of any Python object.

    Handles both hashable and unhashable objects. For general-purpose cryptographic needs, SHA-256 is often the best
    choice due to its balance of security, speed, and widespread adoption.

    Input:
    - A `str` is hashed as its UTF-8 encoding.
    - A `bytes`, `bytearray` or `memoryview` is hashed as its raw content, so the digest matches the one produced by
      standard tooling (`sha1sum`, another language, a stored ETag, ...) for the same payload.
    - Any other object is serialised with `pickle` first, which makes the digest specific to Python.

    Output:
    - The function returns the hash as a hexadecimal string, making it suitable for storage and comparison.
    - This approach ensures the function works for a broad range of Python objects.

    Parameters
    ----------
    obj : Any
        The Python object to hash.
    alg : str, optional
        Hashing algorithm to use (default is sha256).

    Returns
    -------
    str
        A hexadecimal string representing the hash of the object.
    """
    # Check if the requested algorithm is supported and avaiable by hashlib
    # https://docs.python.org/3/library/hashlib.html
    if alg not in hashlib.algorithms_guaranteed:
        raise ValueError(f"Hashing algorithm '{alg}' not supported. Supported: {hashlib.algorithms_guaranteed}.")
    hasher = hashlib.new(alg, usedforsecurity=False)
    if isinstance(obj, str):
        hasher.update(obj.encode())
    elif isinstance(obj, bytes | bytearray | memoryview):
        hasher.update(obj)
    else:
        bytes_: bytes = pickle.dumps(obj, protocol=3)
        hasher.update(bytes_)
    if alg in {"shake_128", "shake_256"}:
        return hasher.hexdigest(length=64)  # ty: ignore[unknown-argument]
    return hasher.hexdigest()

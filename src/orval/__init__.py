"""Orval package."""

from importlib import metadata

from orval.arrays import chunkify, flatten
from orval.byte_utils import pretty_bytes
from orval.datetimes import utcnow
from orval.hashing import hashify
from orval.strings import camel_case, kebab_case, pascal_case, slugify, snake_case, train_case, truncate
from orval.utils import timing

__version__ = metadata.version(__package__)
__all__ = [
    "camel_case",
    "chunkify",
    "flatten",
    "hashify",
    "kebab_case",
    "pascal_case",
    "pretty_bytes",
    "slugify",
    "snake_case",
    "timing",
    "train_case",
    "truncate",
    "utcnow",
]

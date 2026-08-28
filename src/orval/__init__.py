"""Orval package."""

from importlib import metadata

from orval.byte_utils import pretty_bytes
from orval.coercion import safe_float, safe_int, to_bool
from orval.containers import chunkify, deep_merge, flatten, pick
from orval.datetimes import utcnow
from orval.duration_utils import pretty_duration
from orval.hashing import hashify
from orval.strings import (
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
from orval.utils import timing

__version__ = metadata.version(__package__)  # ty: ignore[invalid-argument-type]
__all__ = [
    "camel_case",
    "chunkify",
    "deep_merge",
    "dot_case",
    "flatten",
    "hashify",
    "kebab_case",
    "mask",
    "pascal_case",
    "pick",
    "pretty_bytes",
    "pretty_duration",
    "safe_float",
    "safe_int",
    "slugify",
    "snake_case",
    "strip_accents",
    "strip_styling",
    "timing",
    "to_bool",
    "train_case",
    "truncate",
    "utcnow",
]

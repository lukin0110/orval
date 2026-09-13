"""Orval package."""

from importlib import metadata

from orval.byte_utils import parse_bytes, pretty_bytes
from orval.coercion import safe_float, safe_int, to_bool
from orval.containers import (
    chunkify,
    compact,
    deep_get,
    deep_merge,
    deep_set,
    flatten,
    is_empty,
    omit,
    pick,
    unique,
)
from orval.datetimes import to_tz, to_utc, utcnow
from orval.duration_utils import parse_duration, pretty_duration
from orval.hashing import hashify
from orval.number_utils import pretty_number
from orval.strings import (
    camel_case,
    dot_case,
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
from orval.token_utils import estimate_tokens, truncate_tokens
from orval.utils import coalesce, coalesce_lazy, timing

__version__ = metadata.version(__package__)  # ty: ignore[invalid-argument-type]
__all__ = [
    "camel_case",
    "chunkify",
    "coalesce",
    "coalesce_lazy",
    "compact",
    "deep_get",
    "deep_merge",
    "deep_set",
    "dot_case",
    "estimate_tokens",
    "flatten",
    "has_control",
    "hashify",
    "is_empty",
    "kebab_case",
    "mask",
    "omit",
    "parse_bytes",
    "parse_duration",
    "pascal_case",
    "pick",
    "pretty_bytes",
    "pretty_duration",
    "pretty_number",
    "safe_float",
    "safe_int",
    "slugify",
    "snake_case",
    "squish",
    "strip_accents",
    "strip_control",
    "strip_styling",
    "timing",
    "to_bool",
    "to_tz",
    "to_utc",
    "train_case",
    "truncate",
    "truncate_bytes",
    "truncate_tokens",
    "unique",
    "utcnow",
]

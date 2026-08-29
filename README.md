[![Lint and Test](https://github.com/lukin0110/orval/actions/workflows/test.yml/badge.svg)](https://github.com/lukin0110/orval/actions)

# Orval (beta)

A Python package containing a small set of utility functions not found in Python's standard library. It is lightweight, written in pure Python, and has no dependencies.

Why is it named `orval`? Because other utility names are boring and it's a tasty [Belgian beer](https://en.wikipedia.org/wiki/Orval_Brewery) 🤘❤️

## 🚀 Using

To install this package, run:
```bash
pip install orval
```

### String utils
```python
from orval import kebab_case

kebab_case("Great Scott")
# Output: great-scott
kebab_case("Gréat Scött")
# Output: gréat-scött
```

```python
# Slightly different from kebab_case. It does not allow Unicode characters.
# Slugify is well-suited for URL paths or infrastructure resource names (e.g., database names).
from orval import slugify

slugify("Great scott !! 🤘")
# Output: great-scott
slugify("Gréat scött !! 🤘")
# Output: great-scott
```

```python
from orval import camel_case

camel_case(" Great scott ")
# Output: greatScott
```

```python
from orval import snake_case

snake_case(" Great  Scott ")
# Output: great_scott
```

```python
# Train-Case is well-suited for HTTP headers.
from orval import train_case

train_case(" content type ")
# Output: Content-Type
```

```python
# Strip styling (HTML tags, entities, Unicode-styled chars) from copy/pasted text.
from orval import strip_styling

strip_styling("<b>𝐡𝐞𝐥𝐥𝐨</b> &amp; <i>𝑤𝑜𝑟𝑙𝑑</i>")
# Output: hello & world
strip_styling("𝓯𝓪𝓷𝓬𝔂 café")
# Output: fancy café
```

```python
# Remove accents/diacritics while preserving non-Latin scripts.
from orval import strip_accents

strip_accents("Héllo Wörld")
# Output: Hello World
strip_accents("café こんにちは")
# Output: cafe こんにちは
```

```python
# Redact sensitive values (API keys, tokens, card numbers) while keeping a few
# characters visible. Strings with 'show' or fewer characters are fully masked.
from orval import mask

mask("sk-abc123xyz", show=4)
# Output: ********3xyz
mask("sk-abc123xyz", show=4, side="l")
# Output: sk-a********
mask("abc", show=4)
# Output: ***
```

### Collection utils

```python
from orval import chunkify

chunkify([1, 2, 3, 4, 5, 6], 2)
# Output: [[1, 2], [3, 4], [5, 6]]
```

```python
from orval import flatten

list(flatten([[1, 2], [3, [4]]]))
# Output: [1, 2, 3, 4]
list(flatten([[1, 2], [3, [4]]], depth=1))
# Output: [1, 2, 3, [4]]
list(flatten([{1, 2}, [{3}, (4,)]]))
# Output: [1, 2, 3, 4]
```

```python
# Drop None values, or all falsy values, from an iterable or the given arguments.
from orval import compact

compact([0, 1, None, 2, False, 3, ""])
# Output: [0, 1, 2, False, 3, '']
compact(0, 1, None, 2)
# Output: [0, 1, 2]
compact([0, 1, None, 2, False, 3, ""], none_only=False)
# Output: [1, 2, 3]
```

```python
# Check whether a value is empty: None or a sized container without elements.
# Unlike truthiness, 0 and False are not empty.
from orval import is_empty

is_empty(None)
# Output: True
is_empty([])
# Output: True
is_empty("")
# Output: True
is_empty(0)
# Output: False
is_empty(False)
# Output: False
```

```python
from orval import pick

pick({"a": {"b": [1, 2, 3], "c": 4}, "d": 5}, "a.b[0]", "d")
# Output: {'a': {'b': {0: 1}}, 'd': 5}
pick({"a": {"b": 1, "c": 2}}, "a.c", "a.x")
# Output: {'a': {'c': 2}}
```

```python
# The opposite of pick: drop nested paths, keep everything else.
from orval import omit

omit({"a": {"b": 1, "c": 2}, "d": 5}, "a.b")
# Output: {'a': {'c': 2}, 'd': 5}
omit({"a": [10, 20, 30]}, "a[1]")
# Output: {'a': [10, 30]}
```

```python
from orval import deep_get

deep_get({"a": {"b": [1, 2, 3]}}, "a.b[0]")
# Output: 1
deep_get({"a": {"b": 1}}, "a.x", default=42)
# Output: 42
```

```python
# Returns a new dictionary, creating intermediate dictionaries as needed.
from orval import deep_set

deep_set({"a": {"b": 1}}, "a.c", 2)
# Output: {'a': {'b': 1, 'c': 2}}
deep_set({}, "a.b[0]", 1)
# Output: {'a': {'b': {0: 1}}}
```

### Misc utils
```python
# Hash any Python object.
from orval import hashify

hashify("great scott")
# Output: 6617ae826b0b76ba9f3a568a2bbf6c67aec8f575eec69badaf7110091d3f5cc6
hashify({"great": "scott"})
# Output: 1d63b966aa065f76392c3e4a7caa7b1bfce39c889e5faf0df0198b9ff5d0f434

def marty():
    return "McFly"

hashify(marty)
# Output: f2f21c93c543f023db0ab78ded26bbc5dabb59bb65b0b458b503cdcb0c3389e4
```

```python
from orval import pretty_bytes

pretty_bytes(1000)
# Output: 1.00 KB (The "human" decimal format, using base 1000)
pretty_bytes(1000, "bs")
# Output: 1000.00 B (Binary format, using base 1024)
pretty_bytes(20000000, "dl", precision=0)
# Output: 20 Megabytes
pretty_bytes(20000000, "bl", precision=0)
# Output: 19 Mebibytes
```

```python
from orval import parse_bytes

parse_bytes("1.5 GiB")
# Output: 1610612736
parse_bytes("1.54 KB")
# Output: 1540
parse_bytes("20 Megabytes")
# Output: 20000000
parse_bytes("512")
# Output: 512 (a bare number is interpreted as bytes)
```

```python
# Coerce loosely-typed input (env vars, query params, config files).
from orval import safe_float, safe_int, to_bool

to_bool("yes")
# Output: True
to_bool("off")
# Output: False
safe_int("3.7")
# Output: 3
safe_int("oops", default=0)
# Output: 0
safe_float("3.14")
# Output: 3.14
safe_float(None, default=1.0)
# Output: 1.0
```

```python
# First value that is not None (like SQL's COALESCE, or chaining ?? in JS).
# Unlike `a or b or c`, falsy values such as 0, "" and False are kept.
from orval import coalesce, coalesce_lazy

coalesce(None, None, 0, 5)
# Output: 0
coalesce(None, None, 8080)
# Output: 8080

# The lazy variant takes callables, so expensive fallbacks only run when needed.
coalesce_lazy(lambda: cache.get(key), lambda: db.fetch(key))
```

```python
from orval import pretty_duration

pretty_duration(9000)
# Output: 2h 30m
pretty_duration(9000, "l")
# Output: 2 hours 30 minutes
pretty_duration(93784)
# Output: 1d 2h 3m 4s
pretty_duration(0.000042)
# Output: 42µs
```

```python
# The inverse of pretty_duration.
from orval import parse_duration

parse_duration("1h30m")
# Output: 5400.0
parse_duration("2 hours 30 minutes")
# Output: 9000.0
parse_duration("250ms")
# Output: 0.25
parse_duration("90")
# Output: 90.0 (a bare number is interpreted as seconds)
```

```python
from orval import pretty_number

pretty_number(1234567)
# Output: 1.2M
pretty_number(1234567, "l")
# Output: 1.2 million
pretty_number(1234567890)
# Output: 1.2B
pretty_number(1234567, precision=2)
# Output: 1.23M
pretty_number(999)
# Output: 999
```

See all available functions in [\_\_init\_\_.py](src/orval/__init__.py).

## 🧑‍💻 Contributing

<details>
<summary>Prerequisites</summary>

<details>
<summary>1. Install Docker</summary>

1. Go to [Docker](https://www.docker.com/get-started), download and install docker.
2. [Configure Docker to use the BuildKit build system](https://docs.docker.com/build/buildkit/#getting-started). On macOS and Windows, BuildKit is enabled by default in Docker Desktop.

</details>

<details>
<summary>2. Install VS Code</summary>

Go to [VS Code](https://code.visualstudio.com/), download and install VS Code.
</details>

</details>

#### 1. Open DevContainer with VS Code
Open this repository with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.

The following commands can be used inside a DevContainer.

#### 2. Run linters
```bash
poe lint
```

#### 3. Run tests
```bash
poe test
```

#### 4. Update uv lock file
```bash
uv lock
```

---
See how to develop with [PyCharm or any other IDE](https://github.com/lukin0110/uv-copier/tree/main/docs/ide.md).

---
️⚡️ Scaffolded with [Uv Copier](https://github.com/lukin0110/uv-copier/).\
🛠️ [Open an issue](https://github.com/lukin0110/uv-copier/issues/new) if you have any questions or suggestions.

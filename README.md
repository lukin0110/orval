[![Lint and Test](https://github.com/lukin0110/orval/actions/workflows/test.yml/badge.svg)](https://github.com/lukin0110/orval/actions)

# Orval (beta)

A Python package containing a small set of utility functions not found in Python's standard library. It is lightweight, written in pure Python, and has no dependencies.

Why is it named `orval`? Because other utility names are boring and it's a tasty [Belgian beer](https://en.wikipedia.org/wiki/Orval_Brewery) 🤘❤️

## 🚀 Using

To install this package, run:
```bash
pip install orval
```

Example usage:
```python
from orval import camel_case
camel_case("Great scott")
# Output: greatScott
```

```python
from orval import kebab_case
kebab_case("Great Scott")
# Output: great-scott
```

```python
from orval import snake_case
snake_case("Great Scott")
# Output: great_scott
```

```python
from orval import slugify
slugify("Great scott !! 🤘")
# Output: great-scott
```

```python
from orval import chunkify
chunkify([1, 2, 3, 4, 5, 6], 2)
# Output: [[1, 2], [3, 4], [5, 6]]
```

```python
from orval import pretty_bytes
pretty_bytes(1000)
# Output: 1.00 KB (The "human" decimal format, using base 1000)
pretty_bytes(1000, "bs")
# Output: 1000.00 B (Binary format, using base 1024)
pretty_bytes(20000000, "dl", precision=0)
# Output: 20 Megabytes
pretty_bytes(20000000, "dl", precision=0)
# Output: 19 Mebibytes
```

See all available functions in [__init__.py](src/orval/__init__.py).

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

#### 4. Update poetry lock file
```bash
poetry lock --no-update
```

---
See how to develop with [PyCharm or any other IDE](https://github.com/lukin0110/poetry-copier/tree/main/docs/ide.md).

---
️⚡️ Scaffolded with [Poetry Copier](https://github.com/lukin0110/poetry-copier/).\
🛠️ [Open an issue](https://github.com/lukin0110/poetry-copier/issues/new) if you have any questions or suggestions.

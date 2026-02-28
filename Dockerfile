# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.14.3
FROM python:$PYTHON_VERSION-slim AS base

LABEL org.opencontainers.image.description="A Python package that contains a small set of convenient python functions"

# Configure Python to print tracebacks on crash [1], and to not buffer stdout and stderr [2].
# [1] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONFAULTHANDLER
# [2] https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

# Install uv.
ENV UV_VERSION=0.10.7
RUN --mount=type=cache,target=/root/.cache/pip/ \
    pip install uv==$UV_VERSION

# Install curl & compilers that may be required for certain packages or platforms.
# The stock ubuntu image cleans up /var/cache/apt automatically. This makes the build process slow.
# Enable apt caching by removing docker-clean
RUN rm /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && apt-get install --no-install-recommends --yes curl build-essential

# Create and activate a virtual environment.
# https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV

# Set the working directory.
WORKDIR /workspaces/orval/

# Touch minimal files to allow uv to install dependencies.
RUN mkdir -p /root/.cache/uv && mkdir -p src/orval/ && touch src/orval/__init__.py && touch README.md



FROM base AS dev

# Install DevContainer utilities: zsh, git, docker cli, starship prompt.
# Docker: only docker cli is installed and not the entire engine.
RUN --mount=type=cache,target=/var/cache/apt/ \
    --mount=type=cache,target=/var/lib/apt/ \
    apt-get update && apt-get install --yes --no-install-recommends openssh-client git zsh gnupg  && \
    # Install docker cli (based on https://get.docker.com/)
    install -m 0755 -d /etc/apt/keyrings && \
    curl -fsSL "https://download.docker.com/linux/debian/gpg" | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg && \
    chmod a+r /etc/apt/keyrings/docker.gpg && \
    apt_repo="deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" && \
    echo "$apt_repo" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && apt-get --yes --no-install-recommends install docker-ce-cli docker-compose-plugin && \
    # Install starship prompt
    sh -c "$(curl -fsSL https://starship.rs/install.sh)" -- "--yes" && \
    # Mark the workspace as safe for git
    git config --system --add safe.directory '*'

# Install the run time Python dependencies in the virtual environment.
COPY uv.lock* pyproject.toml /workspaces/orval/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --all-extras --frozen --compile-bytecode --link-mode copy --python-preference only-system

# Install pre-commit hooks & activate starship.
COPY .pre-commit-config.yaml /workspaces/orval/
RUN git init && pre-commit install --install-hooks && \
    echo 'eval "$(starship init zsh)"' >> ~/.zshrc && \
    echo 'poe --help' >> ~/.zshrc && \
    zsh -c 'source ~/.zshrc'

CMD ["zsh"]




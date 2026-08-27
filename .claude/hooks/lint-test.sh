#!/usr/bin/env bash
# Stop hook: run lint & test once per change to the package sources.
#
# Fingerprints src/, tests/ and the tool configs; skips when nothing changed
# since the last run (this also breaks the Stop -> block -> Stop loop when
# Claude stops again without editing anything). Exits 2 on failure so the
# output is fed back to Claude as a blocking error.
set -uo pipefail

root="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$root" || exit 0

fingerprint() {
    {
        find src tests -type f -not -path '*__pycache__*' -print0 2>/dev/null | sort -z | xargs -0 shasum 2>/dev/null
        shasum pyproject.toml .pre-commit-config.yaml uv.lock 2>/dev/null
    } | shasum | cut -d' ' -f1
}

cache_dir="${TMPDIR:-/tmp}/claude-lint-test-hook/$(printf '%s' "$root" | shasum | cut -d' ' -f1)"
mkdir -p "$cache_dir"
marker="$cache_dir/last-checked"

current=$(fingerprint)
if [ -f "$marker" ] && [ "$(cat "$marker")" = "$current" ]; then
    printf '{"suppressOutput": true}\n'
    exit 0
fi

run_step() {
    local name="$1"
    shift
    local output status
    output=$("$@" 2>&1)
    status=$?
    if [ "$status" -ne 0 ]; then
        # Record the state that failed so an unchanged re-stop is not blocked again.
        printf '%s' "$current" > "$marker"
        printf '%s failed (exit %d):\n\n%s\n' "$name" "$status" "$(printf '%s\n' "$output" | tail -n 60)" >&2
        exit 2
    fi
}

run_step "Lint (uv run poe lint)" uv run poe lint
# Linting may have auto-fixed files; refresh the fingerprint before recording.
run_step "Tests (uv run poe test)" uv run poe test

fingerprint > "$marker"
printf '{"suppressOutput": true, "systemMessage": "Lint & tests passed"}\n'

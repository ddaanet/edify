# Dev tooling from uv.lock (`uv sync`) and package.json (`npm install`).
# Every recipe puts `.venv/bin` and `node_modules/.bin` on PATH itself, so it
# does not depend on direnv having loaded `.envrc`.

import 'plugin-dev/release.just'
import 'plugin-dev/gates.just'

# Commit gate: toolkit checks, markdown wrapping, lint, types, tests, manifest
precommit: check-refs check-size check-frontmatter check-modes
    #!/usr/bin/env bash
    set -euo pipefail
    export PATH="$PWD/.venv/bin:$PWD/node_modules/.bin:$PATH"
    # remark-cli drives test_full_pipeline_remark, which skips without it.
    command -v remark >/dev/null || { echo "precommit: remark not on PATH — run 'npm install'" >&2; exit 1; }
    # `fmt --check` exits 1 exactly when `fmt` would rewrite a file. Plain
    # `rumdl check` also reports over-column lines MD013 cannot reflow.
    # Tracked files only, so an untracked note in scope cannot fail the gate.
    # rumdl skips .rumdl.toml's include for explicit paths: the scope is
    # restated here as pathspecs, where a glob `*` does not cross `/`.
    git ls-files -z -- ':(glob)skills/**/*.md' ':(glob)agents/**/*.md' \
        ':(glob)docs/**/*.md' ':(glob)*.md' | xargs -0 rumdl fmt --check -q --no-cache
    echo "rumdl: tracked markdown wrapped"
    ruff check -q
    echo "ruff: lint clean"
    ruff format --check -q
    echo "ruff: formatted"
    mypy
    echo "mypy: types check"
    pytest -q
    jq . .claude-plugin/plugin.json >/dev/null
    echo "jq: plugin.json parses"

# The gate `just release` runs
prerelease: precommit

# Apply ruff fixes and formatting, and rumdl's markdown wrapping
format:
    #!/usr/bin/env bash
    set -euo pipefail
    export PATH="$PWD/.venv/bin:$PATH"
    ruff check -q --fix-only
    ruff format -q
    rumdl fmt -q --no-cache

# Run the test suite; arguments go to pytest
[positional-arguments]
test *ARGS:
    #!/usr/bin/env bash
    set -euo pipefail
    export PATH="$PWD/.venv/bin:$PWD/node_modules/.bin:$PATH"
    pytest "$@"

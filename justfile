# Justfile Rules:
# - Errors should not pass silently without good reason
# - Only use `2>/dev/null` for probing (checking exit status when command has no quiet option)
# - Only use `|| true` to continue after expected failures (required with `set -e`)

import 'plugin/portable.just'

set allow-duplicate-recipes
set allow-duplicate-variables

# To enable bash tracing (set -x): just trace=true <recipe>
trace := "false"

# List available recipes
help:
    @just --list --unsorted

# Remove generated build artifacts
[no-exit-message]
clean:
    #!{{ bash_prolog }}
    visible rm -rf dist
    echo "${GREEN}✓${NORMAL} Clean"

# Set up development environment (venv, direnv, npm)
[no-exit-message]
setup:
    #!{{ bash_prolog }}
    visible uv sync
    visible npm install
    visible direnv allow

# Verify the plugin's SessionStart bootstrap against a locally built wheel
[no-exit-message]
bootstrap-check:
    #!{{ bash_prolog }}
    visible uv build --wheel --out-dir dist
    data="$PWD/tmp/bootstrap-check"
    visible rm -rf "$data"
    mkdir -p "$data"
    # Install from the local wheel, not PyPI: dogfooding never needs a publish.
    export UV_FIND_LINKS="$PWD/dist"
    visible env CLAUDE_PLUGIN_ROOT="$PWD/plugin" CLAUDE_PLUGIN_DATA="$data" \
        plugin/bin/bootstrap-venv.sh
    visible "$data/current/bin/edify" --version
    report-end-safe "Bootstrap"

# Check file line limits
[no-exit-message]
line-limits:
    #!{{ bash_prolog }}
    sync
    run-line-limits
    report-end-safe "Line limits"

# Check docs/decisions.md and docs/references/*.md crosslink invariants
[no-exit-message]
design-links:
    #!{{ bash_prolog }}
    sync
    run-design-links
    report-end-safe "Design links"

# `precommit` and `dev` are defined in plugin/portable.just, which ships to
# other projects that have no docs/decisions.md or docs/references/ — the
# design-links check does not belong there. This overrides portable.just's
# `precommit` (via `set allow-duplicate-recipes`, same mechanism this file
# already uses to override its shared `bash_prolog`) to add `run-design-links`
# for this repo only; `dev: format precommit` picks it up automatically, since
# `just` resolves a recipe dependency by name against the final recipe set.
# Run all checks
[no-exit-message]
precommit:
    #!{{ bash_prolog }}
    sync
    run-checks
    report "version consistency" python3 plugin/bin/check-version-consistency.py
    run-pytest
    # Non-fixing: `fmt --check` exits 1 exactly when `fmt` would rewrite a
    # file, and `-q` drops the summary so a clean run prints nothing. Plain
    # `rumdl check` is not equivalent — it also reports the over-column lines
    # MD013 cannot reflow, which no `fmt` pass can clear.
    report "rumdl" rumdl fmt --check -q --no-cache
    run-line-limits
    run-design-links
    report-end-safe "Precommit"

# Create release: bump plugin.json (SOT), sync pyproject.toml, tag, push,
# publish to PyPI, GitHub release, bump the marketplace entry.
[no-exit-message]
release BUMP="patch": dev
    #!{{ bash_prolog }}
    visible scripts/release.sh "{{ BUMP }}"

# Complete a release that landed only partially. Idempotent, no gate.
[no-exit-message]
resume-release:
    #!{{ bash_prolog }}
    visible scripts/release.sh --resume

# Bash prolog
[private]
bash_prolog := \
    ( if trace == "true" { "/usr/bin/env bash\nset -xeuo pipefail" } \
    else { "/usr/bin/env bash\nset -euo pipefail" } ) + "\n" + '''
export PATH="$PWD/node_modules/.bin:$PATH"
COMMAND="''' + style('command') + '''"
ERROR="''' + style('error') + '''"
RED=$'\033[31m'
GREEN=$'\033[32m'
NORMAL="''' + NORMAL + '''"
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${ERROR}$*${NORMAL}"; exit 1; }
wt-path() {
    local parent
    parent="$(cd .. && basename "$PWD")"
    if [[ "$parent" == *-wt ]]; then
        echo "$(cd .. && pwd)/$1"
    else
        echo "$(cd .. && pwd)/$(basename "$PWD")-wt/$1"
    fi
}
add-sandbox-dir() {
    local dir="$1" settings="$2"
    mkdir -p "$(dirname "$settings")"
    python3 -c "
import json, sys, os
path = sys.argv[1]
settings_file = sys.argv[2]
data = {}
if os.path.exists(settings_file):
    with open(settings_file) as f:
        data = json.load(f)
dirs = data.setdefault('permissions', {}).setdefault('additionalDirectories', [])
if path not in dirs:
    dirs.append(path)
    with open(settings_file, 'w') as f:
        json.dump(data, f, indent=2)
        f.write('\n')
" "$dir" "$settings"
}

# Do not uv sync when in Claude Code sandbox
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
set-tmpfile() {
    if [[ ! -v tmpfile ]]; then
        tmpfile=$(mktemp tmp/justfile-XXXXXX)
        trap "rm $tmpfile" EXIT
    fi
}

HEADER_STYLE=$'\033[1;36m'  # Bold cyan
report () {
    # Usage: report "header" command args
    header=$1; shift
    set-tmpfile
    safe "$@" &> "$tmpfile"
    if [ -s "$tmpfile" ]; then
        echo "${HEADER_STYLE}# $header${NORMAL}"
        cat "$tmpfile"
    fi
}

run-checks() {
    report "ruff check" ruff check -q
    report "ruff format --check" ruff format --check -q
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}

run-lint-checks() {
    ruff_ignores=C901,PLR0904,PLR0911,PLR0912,PLR0913,PLR0914,PLR0915,PLR0916,PLR0917,PLR1701,PLR1702
    report "ruff check" ruff check -q --ignore=$ruff_ignores
    # `check` has no `format` dependency, so without this `just check` is the
    # one checking recipe that never notices unformatted code. Redundant but
    # free under `lint`/`green`/`red-lint`, which all run `format` first.
    report "ruff format --check" ruff format --check -q
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}

run-pytest() {
    # Test sentinel: skip pytest if inputs unchanged
    local sentinel="tmp/.test-sentinel"
    mkdir -p tmp
    local current_hash
    current_hash=$( {
        python3 --version 2>&1
        # Untracked files count: a new test module is an input before its
        # first commit. scripts/ and the design docs are read by the suite.
        git ls-files -z --cached --others --exclude-standard \
            src/ tests/ scripts/ plugin/hooks/ plugin/bin/ \
            docs/decisions.md docs/references/ | sort -z | xargs -0 cat
        cat pyproject.toml
    } | cksum )
    if [ -f "$sentinel" ] && [ "$(cat "$sentinel")" = "$current_hash" ]; then
        echo "Tests cached (inputs unchanged)"
        return
    fi
    local pytest_output pytest_failed=false
    pytest_output=$(pytest 2>&1) || pytest_failed=true
    echo "$pytest_output"
    if echo "$pytest_output" | grep -q "skipped"; then fail "Tests skipped — all tests must run"; fi
    if [ "$pytest_failed" = true ]; then
        status=false
    else
        echo "$current_hash" > "$sentinel"
    fi
}

run-line-limits() {
    # Wrapped like every other check: `safe` so an overage reaches
    # `report-end-safe` instead of aborting the recipe under `set -e`, and a
    # header so the `oversized-file:` lines an allowlisted file prints on
    # every green run say what produced them.
    report "line limits" ./scripts/check_line_limits.sh
}

run-design-links() {
    report "design links" ./scripts/check_design_links.sh
}

report-end-safe() {
    if end-safe
    then echo "${GREEN}✓$NORMAL $1 OK"
    else echo "${RED}✗$NORMAL $1 failed"
    fi
    end-safe
}
'''

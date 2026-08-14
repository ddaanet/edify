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
    report "docformatter -c" docformatter -c src tests
    report "mypy" mypy
}

run-lint-checks() {
    ruff_ignores=C901,PLR0904,PLR0911,PLR0912,PLR0913,PLR0914,PLR0915,PLR0916,PLR0917,PLR1701,PLR1702
    report "ruff check" ruff check -q --ignore=$ruff_ignores
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
        git ls-files -z src/ tests/ plugin/hooks/ plugin/bin/ | sort -z | xargs -0 cat
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
    ./scripts/check_line_limits.sh
}

report-end-safe() {
    if end-safe
    then echo "${GREEN}✓$NORMAL $1 OK"
    else echo "${RED}✗$NORMAL $1 failed"
    fi
    end-safe
}
'''

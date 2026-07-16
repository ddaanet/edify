# Portable justfile module — distributed with edify plugin
# Import in consuming projects: import 'portable.just'
# Variables merge across import boundaries; root justfile's bash_prolog overrides this one.

# Self-contained bash prolog for portable module (cannot rely on root justfile's bash_prolog)
bash_prolog := "/usr/bin/env bash\nset -euo pipefail\n" + '''
export PATH="$PWD/node_modules/.bin:$PATH"
RED=$'\033[31m'
GREEN=$'\033[32m'
NORMAL=$'\033[0m'
COMMAND=$'\033[1m'
ERROR=$'\033[1;31m'
HEADER_STYLE=$'\033[1;36m'
safe () { "$@" || status=false; }
end-safe () { ${status:-true}; }
show () { echo "$COMMAND$*$NORMAL"; }
visible () { show "$@"; "$@"; }
fail () { echo "${RED}FAIL: $*${NORMAL}" >&2; exit 1; }

# Do not uv sync when in Claude Code sandbox
sync() { if [ -w /tmp ]; then uv sync -q; fi; }
set-tmpfile() {
    if [[ ! -v tmpfile ]]; then
        tmpfile=$(mktemp tmp/justfile-XXXXXX)
        trap "rm $tmpfile" EXIT
    fi
}
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

# Launch Claude Code with plugin loaded from submodule
[no-exit-message]
claude:
    #!{{ bash_prolog }}
    exec claude --plugin-dir ./plugin

# Launch Claude Code with plugin and empty system prompt (clean-slate workflow)
[no-exit-message]
claude0:
    #!{{ bash_prolog }}
    exec claude --plugin-dir ./plugin --system-prompt ""

# Run all checks
[no-exit-message]
precommit:
    #!{{ bash_prolog }}
    sync
    run-checks
    report "version consistency" python3 plugin/bin/check-version-consistency.py
    run-pytest
    run-line-limits
    report-end-safe "Precommit"

# Run test suite
[no-exit-message]
test *ARGS:
    #!{{ bash_prolog }}
    sync
    pytest {{ ARGS }}
    report-end-safe "Tests"

# Format code
format:
    #!{{ bash_prolog }}
    sync
    set-tmpfile
    patch-and-print() {
        patch "$@" | sed -Ene "/^patching file '/s/^[^']+'([^']+)'/\\1/p"
    }
    ruff check -q --fix-only --diff | patch-and-print >> "$tmpfile" || true
    ruff format -q --diff | patch-and-print >> "$tmpfile" || true
    docformatter --diff src tests | patch-and-print -Rp1 >> "$tmpfile" || true
    modified=$(sort --unique < "$tmpfile")
    if [ -n "$modified" ] ; then
        bold=$'\033[1m'; nobold=$'\033[22m'
        red=$'\033[31m'; resetfg=$'\033[39m'
        echo "${bold}${red}**Reformatted files:**"
        echo "$modified" | sed "s|^|${bold}${red}  - ${nobold}${resetfg}|"
    fi

# Format, check without complexity, NO test
[no-exit-message]
red-lint: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    report-end-safe "Red Lint"

# Format, check without complexity, test
[no-exit-message]
lint: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    run-pytest
    report-end-safe "Lint"

# Check code style
[no-exit-message]
check:
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    report-end-safe "Checks"

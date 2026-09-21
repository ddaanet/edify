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
        # first commit.
        git ls-files -z --cached --others --exclude-standard \
            src/ tests/ scripts/ plugin/hooks/ plugin/bin/ | sort -z | xargs -0 cat
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
    # Non-fixing: `fmt --check` exits 1 exactly when `fmt` would rewrite a
    # file, and `-q` drops the summary so a clean run prints nothing. Plain
    # `rumdl check` is not equivalent — it also reports the over-column lines
    # MD013 cannot reflow, which no `fmt` pass can clear.
    report "rumdl" rumdl fmt --check -q --no-cache
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
        # `patch` prints `patching file PATH` in both forward and reverse
        # mode, shell-quoting PATH only when it has to (`patching file 'has
        # space.txt'`). Accept either form. Residual bound: a name containing
        # a literal single quote comes back carrying patch's own `'\''`
        # escaping.
        patch "$@" | sed -Ene "s/^patching file '?([^']*)'?$/\1/p"
    }
    apply-ruff-diff() {
        # `ruff --diff`'s diff header carries no `a/`/`b/` prefix, so this
        # needs `-p0`: bare `patch` cannot auto-detect that and, given
        # non-tty stdin, silently skips every hunk instead of applying it.
        # ruff exits 1 for "diffs to show" (a result) and 2 for a tool
        # error; tolerate the former, fail on the latter. A `patch` failure
        # — a hunk it cannot apply — must fail loudly too rather than vanish
        # into the pipeline's status. Residual bound: ruff writes a bare
        # `--- PATH` header with no tab, so for a path containing a space
        # `patch` reads the name up to the space and the hunk fails. That is
        # a loud failure here by design, not silent skipping.
        local label="$1"; shift
        set +e
        "$@" | patch-and-print -p0 >> "$tmpfile"
        local status=("${PIPESTATUS[@]}")
        set -e
        [ "${status[0]}" -le 1 ] || fail "$label: ruff exited ${status[0]}"
        [ "${status[1]}" -eq 0 ] || fail "$label: patch failed to apply (exit ${status[1]})"
    }
    apply-ruff-diff "ruff check --fix-only --diff" ruff check -q --fix-only --diff
    apply-ruff-diff "ruff format --diff" ruff format -q --diff
    # `pyproject.toml` sets `in-place = true`, so docformatter has already
    # rewritten the files by the time it prints its diff. The diff is only a
    # source of file names here; applying it undoes that rewrite, which is
    # what `-Rp1` did — reverting each file, still listing it as reformatted,
    # and leaving `docformatter -c` to fail on it. Read the names off the
    # `--- before/PATH` headers instead. Exit 3 is "files changed", 0 is
    # "nothing to do"; anything else is a tool error.
    set +e
    docformatter --diff src tests | sed -ne 's|^--- before/||p' >> "$tmpfile"
    df_status=("${PIPESTATUS[@]}")
    set -e
    case "${df_status[0]}" in
    0 | 3) ;;
    *) fail "docformatter --diff: exited ${df_status[0]}" ;;
    esac
    [ "${df_status[1]}" -eq 0 ] || fail "docformatter listing: sed failed (exit ${df_status[1]})"
    # `-q` leaves one `path:line:col: … [fixed]` diagnostic per fix and drops
    # the summary; keep the path so the listing below names the file. Several
    # fixes in one file repeat it — `sort --unique` collapses them.
    rumdl fmt -q --no-cache | sed -Ene '/\[fixed\]$/s/^([^:]+):.*$/\1/p' >> "$tmpfile"
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

# Verify GREEN: format, lint, test (semantic alias for lint)
[no-exit-message]
green *ARGS: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    if [ -n "{{ ARGS }}" ]; then pytest {{ ARGS }}; else run-pytest; fi
    report-end-safe "Green"

# Format and run all checks
[no-exit-message]
dev: format precommit

# Check code style
[no-exit-message]
check:
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    report-end-safe "Checks"

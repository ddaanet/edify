# Justfile Rules:
# - Errors should not pass silently without good reason
# - Only use `2>/dev/null` for probing (checking exit status when command has no quiet option)
# - Only use `|| true` to continue after expected failures (required with `set -e`)

import 'agent-core/portable.just'

set allow-duplicate-recipes
set allow-duplicate-variables

# To enable bash tracing (set -x): just trace=true <recipe>
trace := "false"

# List available recipes
help:
    @just --list --unsorted

# Format and run all checks
[no-exit-message]
dev: format precommit

# Set up development environment (venv, direnv, npm)
[no-exit-message]
setup:
    #!{{ bash_prolog }}
    visible uv sync
    visible npm install
    visible direnv allow

# Check file line limits
[no-exit-message]
line-limits:
    #!{{ bash_prolog }}
    sync
    run-line-limits
    report-end-safe "Line limits"

# Verify GREEN: format, lint, test (semantic alias for lint)
[no-exit-message]
green *ARGS: format
    #!{{ bash_prolog }}
    sync
    run-lint-checks
    if [ -n "{{ ARGS }}" ]; then pytest {{ ARGS }}; else run-pytest; fi
    report-end-safe "Green"

# Create release: tag, build tarball, upload to PyPI and GitHub
# Use --dry-run to perform local changes and verify external permissions without publishing

# Use --rollback to revert local changes from a crashed dry-run
[no-exit-message]
release *ARGS: _fail_if_claudecode dev
    #!{{ bash_prolog }}
    DRY_RUN=false
    ROLLBACK=false
    BUMP=patch
    # Parse flags and positional args
    for arg in {{ ARGS }}; do
        case "$arg" in
            --dry-run) DRY_RUN=true ;;
            --rollback) ROLLBACK=true ;;
            --*) fail "Error: unknown option: $arg" ;;
            *) [[ -n "${positional:-}" ]] && fail "Error: too many arguments"
               positional=$arg ;;
        esac
    done
    [[ -n "${positional:-}" ]] && BUMP=$positional

    # Cleanup function: revert commit and remove build artifacts
    cleanup_release() {
        local initial_head=$1
        local initial_branch=$2
        local version=$3
        visible git reset --hard "$initial_head"
        if [[ -n "$initial_branch" ]]; then
            visible git checkout "$initial_branch"
        else
            visible git checkout "$initial_head"
        fi

        # Remove only this version's build artifacts
        if [[ -n "$version" ]] && [[ -d dist ]]; then
            find dist -name "*${version}*" -delete
            [[ -d dist ]] && [[ -z "$(ls -A dist)" ]] && visible rmdir dist
        fi
    }

    # Rollback mode
    if [[ "$ROLLBACK" == "true" ]]; then
        # Check if there's a release commit at HEAD
        if git log -1 --format=%s | grep -q "🔖 Release"; then
            # Verify no permanent changes (commit not pushed to remote)
            # Skip check if HEAD is detached or has no upstream
            if git symbolic-ref -q HEAD >/dev/null && git rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
                # We're on a branch with upstream - check if release commit is unpushed
                if ! git log @{u}.. --oneline | grep -q "🔖 Release"; then
                    fail "Error: release commit already pushed to remote"
                fi
            fi

            version=$(git log -1 --format=%s | sed -n 's/^Release //p')
            current_branch=$(git symbolic-ref -q --short HEAD || echo "")
            cleanup_release "HEAD~1" "$current_branch" "$version"
            echo "${GREEN}✓${NORMAL} Rollback complete"
        else
            fail "No release commit found"
        fi
        exit 0
    fi

    # Check preconditions
    git diff --quiet HEAD || fail "Error: uncommitted changes"
    current_branch=$(git symbolic-ref -q --short HEAD || echo "")
    [[ -z "$current_branch" ]] && fail "Error: not on a branch (HEAD is detached)"
    main_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
    [[ "$current_branch" != "$main_branch" ]] && fail "Error: must be on $main_branch branch (currently on $current_branch)"
    release=$(uv version --bump "$BUMP" --dry-run)
    tag="v$(echo "$release" | awk '{print $NF}')"
    git rev-parse "$tag" >/dev/null 2>&1 && fail "Error: tag $tag already exists"

    # Interactive confirmation (skip in dry-run)
    if [[ "$DRY_RUN" == "false" ]]; then
        while read -re -p "Release $release? [y/n] " answer; do
            case "$answer" in
                y|Y) break;;
                n|N) exit 1;;
                *) continue;;
            esac
        done
    fi

    if [[ "$DRY_RUN" == "true" ]]; then
        INITIAL_HEAD=$(git rev-parse HEAD)
        INITIAL_BRANCH=$(git symbolic-ref -q --short HEAD || echo "")
        trap 'cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "${version:-}"; exit 1' ERR EXIT
    fi

    # Perform local changes: version bump, commit, build
    visible uv version --bump "$BUMP"
    version=$(uv version --short)
    agent-core/bin/bump-plugin-version.py "$version"
    agent-core/bin/check-version-consistency.py
    git add pyproject.toml uv.lock agent-core/.claude-plugin/plugin.json
    visible git commit -m "🔖 Release $version"
    tag="v$(uv version --short)"
    visible uv build

    if [[ "$DRY_RUN" == "true" ]]; then
        # Verify external permissions
        git push --dry-run || fail "Error: cannot push to git remote"
        [[ -z "${UV_PUBLISH_TOKEN:-}" ]] && fail "Error: UV_PUBLISH_TOKEN not set. Get token from https://pypi.org/manage/account/token/"
        uv publish --dry-run dist/* || fail "Error: cannot publish to PyPI"
        gh auth status >/dev/null 2>&1 || fail "Error: not authenticated with GitHub"

        echo ""
        echo "${GREEN}✓${NORMAL} Dry-run complete: $version"
        echo "  ${GREEN}✓${NORMAL} Git push permitted"
        echo "  ${GREEN}✓${NORMAL} PyPI publish permitted"
        echo "  ${GREEN}✓${NORMAL} GitHub release permitted"

        # Normal cleanup
        trap - ERR EXIT
        cleanup_release "$INITIAL_HEAD" "$INITIAL_BRANCH" "$version"
        echo ""
        echo "Run: ${COMMAND}just release $BUMP${NORMAL}"
        exit 0
    fi

    # Perform external actions
    visible git push
    visible git tag -a "$tag" -m "Release $version"
    visible git push origin "$tag"
    visible uv publish
    visible gh release create "$tag" --title "$version" --generate-notes
    echo "${GREEN}✓${NORMAL} Release $tag complete"

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
        git ls-files -z src/ tests/ agent-core/hooks/ agent-core/bin/ | sort -z | xargs -0 cat
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

# Fail if CLAUDECODE is set
[no-exit-message]
[private]
_fail_if_claudecode:
    #!{{ bash_prolog }}
    if [ "${CLAUDECODE:-}" != "" ]
    then fail "⛔️ Denied: Protected recipe"
    fi

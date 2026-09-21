#!/usr/bin/env bash
# Check that source and markdown files do not exceed their line-count cap.
#
# Usage: check_line_limits.sh [--allowlist FILE] [ROOT]
#
# ROOT defaults to `.`. Caps: 400 lines for a Python file under `src` or
# `tests`, and for markdown, 200 for a file named `SKILL.md`, 400 otherwise.
# Markdown scope is `plugin/`, `docs/` and root-level `*.md`, excluding
# `docs/superpowers/plans/` and `docs/superpowers/specs/` (frozen work).
#
# An allowlist records a per-file ceiling above the path-picked cap: a
# sidecar file `check_line_limits.allow` beside this script by default,
# resolved from this script's own location (never ROOT or CWD), or the
# file named by `--allowlist FILE`. Format: one entry per line, `<path>
# <TAB><ceiling><TAB><note>`; blank lines and lines starting with `#` are
# ignored; `path` is root-relative and matched exactly — no globbing, no
# substring, no basename comparison; `ceiling` is the file's recorded
# line-count ceiling. An allowlisted file over the path-picked cap is
# still reported, but only fails the run if it also exceeds its ceiling;
# the reported number is always the cap, never the ceiling. A missing
# default allowlist file means an empty allowlist; a missing file named
# explicitly by `--allowlist` is a failure to run (exit 2). A path
# containing a TAB cannot be expressed.
#
# Ceilings are maintained by hand and only ratchet down: when a listed file
# shrinks, lower its ceiling to the new count, and delete the entry once the
# file is back under its cap. When a listed file grows past its ceiling the
# gate is red by design — trim the file rather than raising the number.
#
# Exit codes: 0 clean, 1 on any overage, 2 on a failure to run the check.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="."
ALLOWLIST=""
ALLOWLIST_EXPLICIT=0
while [[ $# -gt 0 ]]; do
    case "$1" in
    --allowlist)
        # Explicit arity check: under `set -e`, `shift 2` with a single
        # argument left aborts the script with exit 1 — the overage code —
        # and prints nothing.
        if [ "$#" -lt 2 ]; then
            echo "check_line_limits: --allowlist: missing FILE argument" >&2
            exit 2
        fi
        ALLOWLIST="$2"
        ALLOWLIST_EXPLICIT=1
        shift 2
        ;;
    -*)
        echo "check_line_limits: unknown option: $1" >&2
        exit 2
        ;;
    *)
        ROOT="$1"
        shift
        ;;
    esac
done

if [ "$ALLOWLIST_EXPLICIT" -eq 0 ]; then
    ALLOWLIST="$SCRIPT_DIR/check_line_limits.allow"
fi

# Parse the allowlist before `cd "$ROOT"`: ALLOWLIST may be relative to the
# original CWD (the default is already absolute via SCRIPT_DIR). A missing
# explicit --allowlist is a failure to run; a missing default is silently
# an empty allowlist.
ALLOWLIST_PATHS=()
ALLOWLIST_CEILINGS=()
ALLOWLIST_COUNT=0
if [ -f "$ALLOWLIST" ]; then
    line_no=0
    while IFS=$'\t' read -r entry_path ceiling _note || [ -n "$entry_path" ]; do
        line_no=$((line_no + 1))
        [ -z "$entry_path" ] && continue
        case "$entry_path" in
        \#*) continue ;;
        esac
        if [[ "$entry_path" == *$'\r'* || "$ceiling" == *$'\r'* || "$_note" == *$'\r'* ]]; then
            echo "check_line_limits: $ALLOWLIST: line $line_no: entry has a carriage return (CRLF line ending)" >&2
            exit 2
        fi
        if ! [[ "$ceiling" =~ ^[0-9]+$ ]]; then
            echo "check_line_limits: $ALLOWLIST: line $line_no: ceiling is not an integer: $ceiling" >&2
            exit 2
        fi
        ALLOWLIST_PATHS[ALLOWLIST_COUNT]="$entry_path"
        ALLOWLIST_CEILINGS[ALLOWLIST_COUNT]="$ceiling"
        ALLOWLIST_COUNT=$((ALLOWLIST_COUNT + 1))
    done <"$ALLOWLIST"
elif [ "$ALLOWLIST_EXPLICIT" -eq 1 ]; then
    echo "check_line_limits: --allowlist: no such file: $ALLOWLIST" >&2
    exit 2
fi

# A bad ROOT is a failure to run, not an overage — exit 2, not `cd`'s own 1.
cd "$ROOT" || exit 2

EXIT_CODE=0

# Set CEILING to the allowlist ceiling recorded for $1, or to the empty
# string. A linear scan over two indexed arrays, not an associative array:
# `#!/usr/bin/env bash` is bash 3.2 on macOS, which has no `declare -A`.
lookup_ceiling() {
    local i
    CEILING=""
    for ((i = 0; i < ALLOWLIST_COUNT; i++)); do
        if [ "${ALLOWLIST_PATHS[$i]}" = "$1" ]; then
            CEILING="${ALLOWLIST_CEILINGS[$i]}"
            return
        fi
    done
}

# Report one line and set the exit code if $1 exceeds $2 lines, honouring
# any allowlist ceiling recorded for $1.
check_cap() {
    local file="$1" cap="$2" line_count
    # An unreadable file leaves the tree unchecked: exit 2, since a bare
    # `set -e` abort here would surface as 1 and read as an overage.
    if ! line_count=$(wc -l <"$file"); then
        echo "check_line_limits: cannot read $file" >&2
        exit 2
    fi
    if [ "$line_count" -gt "$cap" ]; then
        echo "oversized-file: $file: $line_count lines > $cap"
        lookup_ceiling "$file"
        if [ -z "$CEILING" ] || [ "$line_count" -gt "$CEILING" ]; then
            EXIT_CODE=1
        fi
    fi
}

# Run `find "$@" -print0`, spooling into a temp file so its exit status is
# observable: a process substitution (`< <(find …)`) discards it, and a
# partial walk — a directory `find` cannot read — then passes for a complete
# one. A pipeline into the loop loses `EXIT_CODE` to the subshell, and
# `mapfile -d ''` is bash 4.4; a temp file is the bash-3.2-safe form, read by
# the caller's own `while` loop since a helper cannot hand a NUL-delimited
# stream back any other way. `find`'s own diagnostic (e.g. "Permission
# denied") passes through to stderr unredirected.
walk() {
    find "$@" -print0 >"$WALK_LIST" || {
        echo "check_line_limits: find failed under $1" >&2
        exit 2
    }
}

# A failed `mktemp` leaves the tree unchecked: exit 2, since a bare `set -e`
# abort on the assignment would surface as 1 and read as an overage. Explicit
# template: BSD `mktemp` has no default one, so a bare `mktemp` is a usage
# error on macOS.
if ! WALK_LIST="$(mktemp "${TMPDIR:-/tmp}/check_line_limits.XXXXXX")"; then
    echo "check_line_limits: cannot create the walk list temp file" >&2
    exit 2
fi
trap 'rm -f "$WALK_LIST"' EXIT

# Python source under src/ and tests/, cap 400.
for dir in src tests; do
    [ -d "$dir" ] || continue
    walk "$dir" -type f -name "*.py"
    while IFS= read -r -d '' file; do
        check_cap "$file" 400
    done <"$WALK_LIST"
done

# Markdown under plugin/, docs/, and root-level *.md; cap 200 for SKILL.md,
# 400 otherwise; docs/superpowers/plans and docs/superpowers/specs excluded.
for dir in plugin docs; do
    [ -d "$dir" ] || continue
    walk "$dir" -type f -name "*.md"
    while IFS= read -r -d '' file; do
        case "$file" in
        docs/superpowers/plans/* | docs/superpowers/specs/*) continue ;;
        esac
        cap=400
        [ "$(basename "$file")" = "SKILL.md" ] && cap=200
        check_cap "$file" "$cap"
    done <"$WALK_LIST"
done

walk . -maxdepth 1 -type f -name "*.md"
while IFS= read -r -d '' file; do
    check_cap "${file#./}" 400
done <"$WALK_LIST"

exit "$EXIT_CODE"

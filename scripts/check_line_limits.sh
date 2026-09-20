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
# explicitly by `--allowlist` is a failure to run (exit 2). Lookup uses a
# bash associative array, so bash 4+ is required (a linear scan would be
# needed to support bash 3.2, which this does not).
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
        ALLOWLIST="${2:-}"
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
declare -A ALLOWLIST_CEILING
if [ -f "$ALLOWLIST" ]; then
    line_no=0
    while IFS=$'\t' read -r entry_path ceiling _note || [ -n "$entry_path" ]; do
        line_no=$((line_no + 1))
        [ -z "$entry_path" ] && continue
        case "$entry_path" in
        \#*) continue ;;
        esac
        if ! [[ "$ceiling" =~ ^[0-9]+$ ]]; then
            echo "check_line_limits: $ALLOWLIST: line $line_no: ceiling is not an integer: $ceiling" >&2
            exit 2
        fi
        ALLOWLIST_CEILING["$entry_path"]="$ceiling"
    done <"$ALLOWLIST"
elif [ "$ALLOWLIST_EXPLICIT" -eq 1 ]; then
    echo "check_line_limits: --allowlist: no such file: $ALLOWLIST" >&2
    exit 2
fi

# A bad ROOT is a failure to run, not an overage — exit 2, not `cd`'s own 1.
cd "$ROOT" || exit 2

EXIT_CODE=0

# Report one line and set the exit code if $1 exceeds $2 lines, honouring
# any allowlist ceiling recorded for $1.
check_cap() {
    local file="$1" cap="$2" line_count ceiling
    # An unreadable file leaves the tree unchecked: exit 2, since a bare
    # `set -e` abort here would surface as 1 and read as an overage.
    if ! line_count=$(wc -l <"$file"); then
        echo "check_line_limits: cannot read $file" >&2
        exit 2
    fi
    if [ "$line_count" -gt "$cap" ]; then
        echo "oversized-file: $file: $line_count lines > $cap"
        ceiling="${ALLOWLIST_CEILING[$file]-}"
        if [ -z "$ceiling" ] || [ "$line_count" -gt "$ceiling" ]; then
            EXIT_CODE=1
        fi
    fi
}

# Python source under src/ and tests/, cap 400.
for dir in src tests; do
    [ -d "$dir" ] || continue
    while IFS= read -r -d '' file; do
        check_cap "$file" 400
    done < <(find "$dir" -type f -name "*.py" -print0)
done

# Markdown under plugin/, docs/, and root-level *.md; cap 200 for SKILL.md,
# 400 otherwise; docs/superpowers/plans and docs/superpowers/specs excluded.
for dir in plugin docs; do
    [ -d "$dir" ] || continue
    while IFS= read -r -d '' file; do
        case "$file" in
        docs/superpowers/plans/* | docs/superpowers/specs/*) continue ;;
        esac
        cap=400
        [ "$(basename "$file")" = "SKILL.md" ] && cap=200
        check_cap "$file" "$cap"
    done < <(find "$dir" -type f -name "*.md" -print0)
done

while IFS= read -r -d '' file; do
    check_cap "${file#./}" 400
done < <(find . -maxdepth 1 -type f -name "*.md" -print0)

exit "$EXIT_CODE"

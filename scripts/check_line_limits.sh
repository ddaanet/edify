#!/usr/bin/env bash
# Check that source and markdown files do not exceed their line-count cap.
#
# Usage: check_line_limits.sh [--allowlist FILE] [ROOT]
#
# ROOT defaults to `.`. Caps: 400 lines for a Python file under `src` or
# `tests`, and for markdown, 200 for a file named `SKILL.md`, 400 otherwise.
# Markdown scope is `plugin/`, `docs/` and root-level `*.md`, excluding
# `docs/superpowers/plans/` and `docs/superpowers/specs/` (frozen work).
# `--allowlist` and per-entry ceilings are not implemented yet (KD-7): the
# option is rejected rather than accepted-and-ignored, so no caller can
# believe an allowlist was honoured.
#
# Exit codes: 0 clean, 1 on any overage, 2 on a failure to run the check.

set -euo pipefail

ROOT="."
while [[ $# -gt 0 ]]; do
    case "$1" in
    --allowlist)
        echo "check_line_limits: --allowlist: not implemented" >&2
        exit 2
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

# A bad ROOT is a failure to run, not an overage — exit 2, not `cd`'s own 1.
cd "$ROOT" || exit 2

EXIT_CODE=0

# Report one line and set the exit code if $1 exceeds $2 lines.
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
        EXIT_CODE=1
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

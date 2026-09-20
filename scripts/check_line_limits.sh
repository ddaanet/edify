#!/usr/bin/env bash
# Check that source and markdown files do not exceed their line-count cap.
#
# Usage: check_line_limits.sh [--allowlist FILE] [ROOT]
#
# ROOT defaults to `.`. Caps: 400 lines for a Python file under `src` or
# `tests`, and for markdown, 200 for a file named `SKILL.md`, 400 otherwise.
# Markdown scope is `plugin/`, `docs/` and root-level `*.md`, excluding
# `docs/superpowers/plans/` and `docs/superpowers/specs/` (frozen work).
# `--allowlist` and per-entry ceilings are not implemented yet (KD-7).

set -euo pipefail

ROOT="."
while [[ $# -gt 0 ]]; do
    case "$1" in
    --allowlist)
        shift 2
        ;;
    *)
        ROOT="$1"
        shift
        ;;
    esac
done

cd "$ROOT"

EXIT_CODE=0

# Report one line and set the exit code if $1 exceeds $2 lines.
check_cap() {
    local file="$1" cap="$2" line_count
    line_count=$(wc -l <"$file")
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

#!/usr/bin/env bash
# Check the crosslink invariants binding the split living design's decision
# index, docs/decisions.md, to its argument nodes, docs/references/*.md. The
# hub, docs/design.md, is deliberately out of scope: its conclusions are prose
# with no ID-bearing form to match against, so nothing here pins it — keep it
# out of the test sentinel's input list too.
#
# Usage: check_design_links.sh [ROOT]
#
# ROOT defaults to `.`. Reads ROOT/docs/decisions.md and
# ROOT/docs/references/*.md.
#
# A node's decision definition is a bolded paragraph lead,
# `**D-<n> — <conclusion>.**`, possibly wrapped across physical lines by
# `just format`'s 80-column reflow. A decisions.md index line is
# `- **D-<n>** — <conclusion>.`, also possibly wrapped, continuation
# indented. A group is `## <Group Name>` then `Argued in
# \`docs/references/<file>.md\`.`. Paragraphs are joined (wrap lines rejoined
# with a single space) before matching, so a wrap never misreports as a
# violation.
#
# Checked, one violation line per finding (`<kind>: <ID or path>: <detail>`):
#   unindexed-decision   — a node's D-<n> has no index line
#   orphan-index-line    — an index D-<n> has no node definition
#   duplicate-definition — a D-<n> defined in more than one node
#   duplicate-index-line — a D-<n> indexed more than once
#   conclusion-mismatch  — the index conclusion does not have the node's
#                          conclusion (trailing period stripped) as a
#                          prefix — not equality: a superseded decision's
#                          index line appends a parenthetical the node's own
#                          lead does not carry
#   missing-node         — a group's `Argued in` path does not resolve to a
#                          real file
#
# A clean run prints one sign-off line naming the counts, never a bare "OK":
#   design-links: N decisions indexed, defined once, conclusions match, M
#   nodes present
#
# Exit codes: 0 clean, 1 on any violation, 2 on a failure to run the check
# (missing docs/decisions.md or docs/references/, or a find/read failure) —
# 2 outranks 1: a run failure is reported instead of whatever violations a
# partial scan could see.
#
# Residual bound: `[^*]*` assumes a node's bolded conclusion never itself
# contains a literal `*`; true of every conclusion in the real tree at the
# time this was written (verified across all D-<n> ids). Portable to macOS
# bash 3.2: no associative arrays, indexed arrays walked by C-style `((i++))`
# loops rather than `"${arr[@]}"` expansion, since expanding an empty array
# under `set -u` aborts pre-4.4 bash.

set -euo pipefail

ROOT="${1:-.}"

# Let `cd` print its own reason (missing, not a directory, unreadable) rather
# than replacing every one of them with a guess.
cd "$ROOT" || {
    echo "check_design_links: cannot enter: $ROOT" >&2
    exit 2
}

if [ ! -f docs/decisions.md ]; then
    echo "check_design_links: missing docs/decisions.md under $ROOT" >&2
    exit 2
fi
if [ ! -d docs/references ]; then
    echo "check_design_links: missing docs/references/ under $ROOT" >&2
    exit 2
fi

# A bad ROOT/find/awk failure leaves the tree unchecked: exit 2, since a
# bare `set -e` abort would surface as 1 and read as "no violations found".
# Explicit template: BSD `mktemp` has no default one, so a bare `mktemp` is
# a usage error on macOS.
TMPL="${TMPDIR:-/tmp}/check_design_links.XXXXXX"
if ! WALK_LIST="$(mktemp "$TMPL")" || ! JOIN_LIST="$(mktemp "$TMPL")"; then
    echo "check_design_links: cannot create a temp file" >&2
    exit 2
fi
trap 'rm -f "$WALK_LIST" "$JOIN_LIST"' EXIT

# Join wrapped markdown paragraphs in $1 into one logical line each, written
# to $JOIN_LIST. A paragraph is bounded by a blank line, an ATX heading, or a
# bullet marker (`- `); any other line is a continuation — plain wrap or a
# bullet's indented second line — appended to the current paragraph with a
# single space. This is what lets a `**D-<n> — ...**` node lead or a
# `- **D-<n>** — ...` index line be matched as one string even when it wraps
# across two physical lines.
join_paragraphs() {
    awk '
        function flush() { if (current != "") { print current; current = "" } }
        /^[ \t]*$/ { flush(); next }
        /^- / { flush(); current = $0; next }
        /^#/ { flush(); current = $0; next }
        {
            line = $0
            sub(/^[ \t]+/, "", line)
            if (current == "") current = line
            else current = current " " line
        }
        END { flush() }
    ' "$1" >"$JOIN_LIST" || {
        echo "check_design_links: cannot read $1" >&2
        exit 2
    }
}

# Run `find "$@" -print0`, spooling into $WALK_LIST so its exit status is
# observable (see scripts/check_line_limits.sh's `walk` for why not a process
# substitution or a pipeline).
walk() {
    find "$@" -print0 >"$WALK_LIST" || {
        echo "check_design_links: find failed under $1" >&2
        exit 2
    }
}

DEF_RE='^\*\*D-([0-9]+) — ([^*]*)\.\*\*'
IDX_RE='^- \*\*D-([0-9]+)\*\* — (.*)\.$'
# Literal backticks in a regex, not command substitution; single quotes are
# correct here.
# shellcheck disable=SC2016
ARGUED_RE='^Argued in `([^`]+)`\.$'
HEADING_RE='^## '

DEF_ID=()
DEF_CONCLUSION=()
DEF_FILE=()
DEF_COUNT=0

walk docs/references -type f -name "*.md"
while IFS= read -r -d '' file; do
    join_paragraphs "$file"
    while IFS= read -r logical; do
        if [[ "$logical" =~ $DEF_RE ]]; then
            DEF_ID[DEF_COUNT]="D-${BASH_REMATCH[1]}"
            DEF_CONCLUSION[DEF_COUNT]="${BASH_REMATCH[2]}"
            DEF_FILE[DEF_COUNT]="$file"
            DEF_COUNT=$((DEF_COUNT + 1))
        fi
    done <"$JOIN_LIST"
done <"$WALK_LIST"

IDX_ID=()
IDX_CONCLUSION=()
IDX_COUNT=0
NODE_PATHS=()
NODE_COUNT=0

current_node=""
join_paragraphs docs/decisions.md
while IFS= read -r logical; do
    if [[ "$logical" =~ $HEADING_RE ]]; then
        current_node=""
        continue
    fi
    if [[ "$logical" =~ $ARGUED_RE ]]; then
        current_node="${BASH_REMATCH[1]}"
        seen=0
        for ((i = 0; i < NODE_COUNT; i++)); do
            if [ "${NODE_PATHS[$i]}" = "$current_node" ]; then
                seen=1
                break
            fi
        done
        if [ "$seen" -eq 0 ]; then
            NODE_PATHS[NODE_COUNT]="$current_node"
            NODE_COUNT=$((NODE_COUNT + 1))
        fi
        continue
    fi
    if [[ "$logical" =~ $IDX_RE ]]; then
        IDX_ID[IDX_COUNT]="D-${BASH_REMATCH[1]}"
        IDX_CONCLUSION[IDX_COUNT]="${BASH_REMATCH[2]}"
        IDX_COUNT=$((IDX_COUNT + 1))
    fi
done <"$JOIN_LIST"

VIOLATIONS=0

# count_def ID / count_idx ID: how many times ID occurs in DEF_ID / IDX_ID,
# and (via FIRST_INDEX) the position of its first occurrence.
count_def() {
    # `j` (not `i`) for the internal scan: `for ((i=0;...))` loop variables
    # are ordinary globals in bash, not scoped to the loop, so an unlocalized
    # `i` here would clobber a caller iterating `DEF_COUNT`/`IDX_COUNT` with
    # its own `for ((i=...))`.
    local id="$1" n=0 j
    FIRST_INDEX=-1
    for ((j = 0; j < DEF_COUNT; j++)); do
        if [ "${DEF_ID[$j]}" = "$id" ]; then
            n=$((n + 1))
            [ "$FIRST_INDEX" -eq -1 ] && FIRST_INDEX=$j
        fi
    done
    COUNT=$n
}

count_idx() {
    local id="$1" n=0 j
    FIRST_INDEX=-1
    for ((j = 0; j < IDX_COUNT; j++)); do
        if [ "${IDX_ID[$j]}" = "$id" ]; then
            n=$((n + 1))
            [ "$FIRST_INDEX" -eq -1 ] && FIRST_INDEX=$j
        fi
    done
    COUNT=$n
}

# unindexed-decision / duplicate-definition, one pass per distinct def id
# (first occurrence only, so a duplicated id is not also double-reported).
for ((i = 0; i < DEF_COUNT; i++)); do
    id="${DEF_ID[$i]}"
    count_def "$id"
    [ "$FIRST_INDEX" -ne "$i" ] && continue
    if [ "$COUNT" -gt 1 ]; then
        echo "duplicate-definition: $id: defined in more than one node"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
    count_idx "$id"
    if [ "$COUNT" -eq 0 ]; then
        echo "unindexed-decision: $id: defined in ${DEF_FILE[$i]} but has no index line in docs/decisions.md"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# orphan-index-line / duplicate-index-line, one pass per distinct index id.
for ((i = 0; i < IDX_COUNT; i++)); do
    id="${IDX_ID[$i]}"
    count_idx "$id"
    [ "$FIRST_INDEX" -ne "$i" ] && continue
    if [ "$COUNT" -gt 1 ]; then
        echo "duplicate-index-line: $id: indexed more than once in docs/decisions.md"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
    count_def "$id"
    if [ "$COUNT" -eq 0 ]; then
        echo "orphan-index-line: $id: indexed in docs/decisions.md but not defined in any node"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

# conclusion-mismatch, only for an id defined exactly once and indexed
# exactly once — an id already flagged duplicate on either side has no
# single pair to compare.
for ((i = 0; i < DEF_COUNT; i++)); do
    id="${DEF_ID[$i]}"
    count_def "$id"
    [ "$COUNT" -ne 1 ] && continue
    count_idx "$id"
    [ "$COUNT" -ne 1 ] && continue
    idx_i="$FIRST_INDEX"
    def_concl="${DEF_CONCLUSION[$i]}"
    idx_concl="${IDX_CONCLUSION[$idx_i]}"
    case "$idx_concl" in
    "$def_concl"*) ;;
    *)
        echo "conclusion-mismatch: $id: node conclusion is not a prefix of the index conclusion"
        VIOLATIONS=$((VIOLATIONS + 1))
        ;;
    esac
done

# missing-node: every distinct `Argued in` path must resolve to a real file.
for ((i = 0; i < NODE_COUNT; i++)); do
    path="${NODE_PATHS[$i]}"
    if [ ! -f "$path" ]; then
        echo "missing-node: $path: referenced by \"Argued in\" but the file does not exist"
        VIOLATIONS=$((VIOLATIONS + 1))
    fi
done

if [ "$VIOLATIONS" -gt 0 ]; then
    exit 1
fi

echo "design-links: $IDX_COUNT decisions indexed, defined once, conclusions match, $NODE_COUNT nodes present"
exit 0

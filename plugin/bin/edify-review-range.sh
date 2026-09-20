#!/usr/bin/env bash
# Establishes the review range for a design/outline artifact and stops on
# conflict (KD-2 in plans/provenance-enforcement-and-routing/outline.md).
#
# Locates the repo from the artifact's directory and resolves every path it
# reads against that repo root, since `Derived from:` values are
# repo-relative. Parses the artifact's `## Provenance` section, in the shape
# `design-content-rules.md` §Provenance Section prescribes: `**Base:**` (a
# 40-hex sha, backtick-quoted) and `**Derived from:**` (`none`, or the
# motivating report followed by ``superseding `<path>` ``). Either value may
# wrap across continuation lines, and either may carry a trailing rationale
# clause after the value — real artifacts write both. The base
# sha comes only from the artifact text — never from `HEAD`, `git log`, or
# `merge-base` — so a script that recomputes it cannot pass this contract.
# Where `Derived from:` names a prior artifact, that artifact's own
# `Base:` is read the same way and compared against this one's.
#
# One verdict line on stdout, per KD-2's table:
#   exit 0   RANGE: <base>..HEAD                          proceed with it
#   exit 1   CONFLICT: base <a> != <b> inherited from <path>   STOP, report both
#   exit 1   NO-PROVENANCE: / UNRESOLVED: <base> / NO-PRIOR: <path>  ask the user
#   other    (nothing on stdout)                            STOP: script failed
set -euo pipefail

# Reads $1's `## Provenance` section, joining each `- **Field:**` bullet with
# its indented continuation lines so a hard-wrapped value (the artifact may
# wrap at 80 columns) reads as one logical line. Only the `## Provenance`
# section is in scope: stop joining at the next `## ` heading. Trailing
# whitespace is stripped per line so the join cannot manufacture a double
# space or leave the last field value with a trailing blank. `[ \t]` rather
# than `[[:space:]]`: the one-true-awk shipped on older macOS reads the
# POSIX class as a plain bracket set of its own characters.
provenance_of() {
    awk '
        /^## Provenance/ { in_section = 1; next }
        in_section && /^## / { in_section = 0 }
        in_section {
            sub(/[ \t]+$/, "")
            if ($0 ~ /^- \*\*/) {
                if (bullet != "") print bullet
                bullet = $0
            } else if (bullet != "" && $0 ~ /^[ \t]+[^ \t]/) {
                sub(/^[ \t]+/, "")
                bullet = bullet " " $0
            } else {
                if (bullet != "") { print bullet; bullet = "" }
            }
        }
        END { if (bullet != "") print bullet }
    ' "$1"
}

# Takes a `- **Base:** ...` bullet line (as `provenance_of` joins it) and
# prints its value's first word, backticks stripped — the value may carry an
# optional trailing rationale clause after the sha. Prints nothing if $1 is
# empty (no such bullet).
base_value_of() {
    [[ -z "$1" ]] && return 0
    local base
    base=$(sed -E 's/^- \*\*Base:\*\* *//' <<<"$1")
    base=${base%% *}
    printf '%s' "${base//\`/}"
}

artifact="${1:-}"
if [[ -z "$artifact" ]]; then
    echo "Usage: edify-review-range.sh <artifact-path>" >&2
    exit 2
fi
if [[ ! -f "$artifact" ]]; then
    echo "edify-review-range.sh: no such artifact: $artifact" >&2
    exit 2
fi

artifact_dir=$(dirname -- "$artifact")
# git's own diagnostic goes to stderr unredirected: capturing it into a
# variable that is never printed would silence it.
if ! root=$(git -C "$artifact_dir" rev-parse --show-toplevel); then
    echo "edify-review-range.sh: not inside a git repo: $artifact_dir" >&2
    exit 2
fi

provenance=$(provenance_of "$artifact")

if [[ -z "$provenance" ]]; then
    echo "NO-PROVENANCE:"
    exit 1
fi

base_line=$(grep -m1 -- '\*\*Base:\*\*' <<<"$provenance" || true)
derived_line=$(grep -m1 -- '\*\*Derived from:\*\*' <<<"$provenance" || true)

if [[ -z "$base_line" ]] || [[ -z "$derived_line" ]]; then
    echo "NO-PROVENANCE:"
    exit 1
fi

base=$(base_value_of "$base_line")
# Take the `Derived from:` value's first word — it may carry an optional
# trailing rationale clause after the value.
derived_from=$(sed -E 's/^- \*\*Derived from:\*\* *//' <<<"$derived_line")

if [[ ! "$base" =~ ^[0-9a-fA-F]{40}$ ]]; then
    echo "UNRESOLVED: $base"
    exit 1
fi

# `--quiet` because a base that names no commit is a verdict, not a script
# failure: the non-zero exit *is* the result and `UNRESOLVED:` carries it.
if ! resolved_base=$(git -C "$root" rev-parse --verify --quiet "${base}^{commit}"); then
    echo "UNRESOLVED: $base"
    exit 1
fi

if [[ "${derived_from%% *}" == "none" ]]; then
    printf 'RANGE: %s..HEAD\n' "$resolved_base"
    exit 0
fi

# The prior artifact is the path following `superseding`, which the
# prescribed value reaches only after naming the motivating report — so the
# marker is searched for anywhere in the value, not anchored at its start.
# Backtick-quoted first, so a path containing spaces stays whole.
# shellcheck disable=SC2016 # single-quoted on purpose: the backticks are
# regex literals to match in the artifact, not command substitution.
superseding_quoted='superseding[[:space:]]+`([^`]+)`'
superseding_bare='superseding[[:space:]]+([^[:space:]]+)'
if [[ "$derived_from" =~ $superseding_quoted ]] ||
    [[ "$derived_from" =~ $superseding_bare ]]; then
    prior_path="${BASH_REMATCH[1]}"
    prior="$root/$prior_path"

    if [[ ! -f "$prior" ]]; then
        echo "NO-PRIOR: $prior_path"
        exit 1
    fi

    prior_provenance=$(provenance_of "$prior")
    prior_base_line=$(grep -m1 -- '\*\*Base:\*\*' <<<"$prior_provenance" || true)
    prior_base=$(base_value_of "$prior_base_line")

    if [[ ! "$prior_base" =~ ^[0-9a-fA-F]{40}$ ]]; then
        echo "NO-PRIOR: $prior_path"
        exit 1
    fi

    if [[ "$resolved_base" == "$prior_base" ]]; then
        printf 'RANGE: %s..HEAD\n' "$resolved_base"
        exit 0
    fi

    printf 'CONFLICT: base %s != %s inherited from %s\n' \
        "$resolved_base" "$prior_base" "$prior_path"
    exit 1
fi

echo "NO-PROVENANCE:"
exit 1

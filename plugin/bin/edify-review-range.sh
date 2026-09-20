#!/usr/bin/env bash
# Establishes the review range for a design/outline artifact and stops on
# conflict (KD-2 in plans/provenance-enforcement-and-routing/outline.md).
#
# Locates the repo from the artifact's directory and resolves every path it
# reads against that repo root, since `Derived from:` values are
# repo-relative. Parses the artifact's `## Provenance` section: `**Base:**`
# (a 40-hex sha, backtick-quoted, possibly wrapped across a continuation
# line) and `**Derived from:**` (`none`, or `superseding <path>`). The base
# sha comes only from the artifact text — never from `HEAD`, `git log`, or
# `merge-base` — so a script that recomputes it cannot pass this contract.
#
# One verdict line on stdout, per KD-2's table:
#   exit 0   RANGE: <base>..HEAD                          proceed with it
#   exit 1   CONFLICT: base <a> != <b> inherited from <path>   STOP, report both
#   exit 1   NO-PROVENANCE: / UNRESOLVED: <base> / NO-PRIOR: <path>  ask the user
#   other    (nothing on stdout)                            STOP: script failed
set -euo pipefail

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
if ! root=$(git -C "$artifact_dir" rev-parse --show-toplevel 2>&1); then
    echo "edify-review-range.sh: not inside a git repo: $artifact_dir" >&2
    exit 2
fi

# Join each `- **Field:**` bullet with its indented continuation lines, so a
# hard-wrapped value (the artifact may wrap at 80 columns) reads as one
# logical line before it is matched. Only the `## Provenance` section is in
# scope: stop joining at the next `## ` heading.
provenance=$(awk '
    /^## Provenance/ { in_section = 1; next }
    in_section && /^## / { in_section = 0 }
    in_section {
        if ($0 ~ /^- \*\*/) {
            if (bullet != "") print bullet
            bullet = $0
        } else if (bullet != "" && $0 ~ /^[[:space:]]+[^[:space:]]/) {
            gsub(/^[[:space:]]+/, "")
            bullet = bullet " " $0
        } else {
            if (bullet != "") { print bullet; bullet = "" }
        }
    }
    END { if (bullet != "") print bullet }
' "$artifact")

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

# shellcheck disable=SC2016 # single-quoted on purpose: \1 and * are sed
# syntax, not shell expansions.
base=$(sed -E 's/^- \*\*Base:\*\* *`?([0-9a-fA-F]{40})`?.*/\1/' <<<"$base_line")
derived_from=$(sed -E 's/^- \*\*Derived from:\*\* *//' <<<"$derived_line")
derived_from=${derived_from%% }

if [[ ! "$base" =~ ^[0-9a-fA-F]{40}$ ]]; then
    echo "UNRESOLVED: $base"
    exit 1
fi

if ! resolved_base=$(git -C "$root" rev-parse --verify "${base}^{commit}" 2>&1); then
    echo "UNRESOLVED: $base"
    exit 1
fi

case "$derived_from" in
    none)
        printf 'RANGE: %s..HEAD\n' "$resolved_base"
        exit 0
        ;;
    superseding\ *)
        # TODO(slices 2-8): resolve the prior artifact's path against $root,
        # read its own `**Base:**`, and compare — matching base emits RANGE,
        # differing base emits CONFLICT, missing/base-less prior emits
        # NO-PRIOR. Not implemented; this slice covers only `Derived from:
        # none`.
        echo "NO-PRIOR: ${derived_from#superseding }"
        exit 1
        ;;
    *)
        echo "NO-PROVENANCE:"
        exit 1
        ;;
esac

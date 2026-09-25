#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# Any change is dirt except three paths dirty by convention (KD-7): `memory`
# (the gitlore submodule, normally ` M`), `.claude/handoff-*.md` (`/handoff`
# and `/precompact` leave it modified or staged) and `inbox/*.md` (briefs
# dropped or updated uncommitted on purpose). Safe to exempt because every
# committing dispatch stages its paths by name and never `git add -A`, so
# exempt dirt never enters a commit. The two-column XY status may hold
# anything, so the pattern matches only the path after it.
# `--untracked-files=all` explodes an untracked `inbox/` into its files, since
# a collapsed `?? inbox/` line is not a path the exemption can judge.
# `git status` must succeed; only grep's exit 1 (every line filtered out) is
# a result rather than a failure, so tolerate that one code and nothing else.
exempt='^.. (memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)$'
porcelain=$(git status --porcelain --untracked-files=all)
if status=$(grep -vE "$exempt" <<<"$porcelain"); then
    :
elif [[ $? -eq 1 ]]; then
    status=""
else
    # Exit 2, never 1: 1 is the DIRTY verdict, and a script failure is not a
    # verdict the caller may remediate against.
    echo "ERROR: filtering git status failed"
    exit 2
fi

if [[ -n "$status" ]]; then
    echo "DIRTY: uncommitted changes"
    echo "$status"
    exit 1
fi
checks="tree clean"

just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}
checks="$checks, just precommit passed"

echo "CLEAN: $checks"
exit 0

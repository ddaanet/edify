#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# Any change is dirt except three paths dirty by convention (KD-7): `memory`
# (the gitlore submodule, normally ` M`), `.claude/handoff-*.md` (`/handoff`
# and `/precompact` leave it modified or staged) and `inbox/*.md` (briefs
# dropped or updated uncommitted on purpose). Safe to exempt because every
# committing dispatch stages its paths by name, never `git add -A`, and
# commits them with `git commit -- <paths>`, so exempt dirt never enters a
# commit, even when already staged. The two-column XY status may hold any
# state but a rename or copy: an `R`/`C` line's `old -> new` is two paths, and
# `inbox/a.md -> b.md` would pass as one exempt path. Git quotes a path holding
# a space or a non-ASCII byte, so the pattern allows the quotes.
# `--untracked-files=all` explodes an untracked `inbox/` into its files, since
# a collapsed `?? inbox/` line is not a path the exemption can judge.
# `git status` must succeed; only grep's exit 1 (every line filtered out) is
# a result rather than a failure, so tolerate that one code and nothing else.
exempt='^[^RC][^RC] "?(memory|\.claude/handoff-[^/]+\.md|inbox/[^/]+\.md)"?$'
porcelain=$(git status --porcelain --untracked-files=all) || {
    echo "ERROR: git status failed"
    exit 2
}
# A pipe, not a here-string: bash writes a here-string to a temp file (always
# before 5.1, above the pipe size after), and a failure to create it also
# exits 1, which would read as "every line filtered out".
if status=$(printf '%s\n' "$porcelain" | grep -vE "$exempt"); then
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

command -v just >/dev/null || {
    echo "ERROR: just not found on PATH"
    exit 2
}
just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}
checks="$checks, just precommit passed"

echo "CLEAN: $checks"
exit 0

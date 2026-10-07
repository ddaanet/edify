#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# Parameter expansion, not `dirname`: `test_missing_just_exits_2` stubs a
# minimal PATH that lacks `dirname`. `BASH_SOURCE[0]` is the invocation path,
# absolute or relative to the CWD (`/build` runs
# `plugin/skills/build/scripts/verify-step.sh` from the repo root); nothing
# changes directory before the source, so both resolve. A symlink to this
# file resolves to the link's directory and fails the source: exit 2.
case "${BASH_SOURCE[0]}" in
    */*) script_dir="${BASH_SOURCE[0]%/*}" ;;
    *) script_dir="." ;;
esac
# A file that sources but leaves the variable unset would trip `set -u`,
# whose exit 1 reads as the DIRTY verdict. The variable is cleared first: an
# inherited value would pass the check when the file defines nothing.
unset EXEMPT_PATHS_ALTERNATION
# shellcheck source=SCRIPTDIR/exempt-paths.sh
if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]; then
    echo "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
    exit 2
fi

# D-91: the exempt alternation lives in exempt-paths.sh (the three paths
# dirty by convention are explained there), shared with changed-files.sh.
# Safe to exempt (D-91) because every committing dispatch stages
# its paths by name, never `git add -A`, and commits them with
# `git commit -- <paths>`, so exempt dirt never enters a commit, even when
# already staged. The two-column XY status may hold any state but a rename
# or copy: an `R`/`C` line's `old -> new` is two paths, and
# `inbox/a.md -> b.md` would pass as one exempt path. Git quotes a path
# holding a space or a non-ASCII byte, so the pattern allows the quotes. The
# status forces `core.quotePath` on: with a user's `false`, a raw non-UTF-8
# byte makes grep call the input binary and drop that line, so its dirt
# would read clean. `--untracked-files=all` explodes an untracked `inbox/`
# into its files, since a collapsed `?? inbox/` line is not a path the
# exemption can judge. `git status` must succeed; only grep's exit 1 (every
# line filtered out) is a result rather than a failure, so tolerate that one
# code and nothing else.
exempt='^[^RC][^RC] "?('"${EXEMPT_PATHS_ALTERNATION}"')"?$'
porcelain=$(git -c core.quotePath=true status --porcelain --untracked-files=all) || {
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
    printf '%s\n' "$status"
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

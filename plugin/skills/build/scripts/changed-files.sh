#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# KD-1: the base is the parent of the earliest commit that added a
# `plans/<job>/reports/item-*` report. `--diff-filter=A --reverse` orders
# additions oldest first; the first line is that commit, and its parent is
# the base. `--no-show-signature` keeps a user's `log.showSignature` from
# printing verification lines ahead of the shas. With no commit adding such
# a report the script prints `NO-BASE:` and exits 1; usage errors and git
# failures exit 2 with `ERROR:`, so nothing else may exit 1.
# KD-6: the changed-files list is the committed diff since that base
# (`<base> HEAD`, never the working tree), minus the job's own
# `plans/<job>/` record and the exempt paths `exempt-paths.sh` names (a run
# commit can also carry a `/handoff` or memory-pointer commit's exempt
# paths, which are not the run's own work). Paths come from a NUL-delimited
# `git diff -z`, read with `read -r -d ''`, never split on whitespace or
# newlines. `--no-renames`, on the diff and the log alike, makes a rename a
# deletion plus an addition whatever the user's `diff.renames`, so a report
# renamed into place counts as added; it also keeps git's skipped-rename
# warning, which `exec 2>&1` would print among the paths, out of stdout.
# The exempt match happens inside that same NUL-delimited read loop, with
# bash's `[[ $path =~ $re ]]` (the regex held in a variable, bash-3.2-safe)
# rather than a second pass through grep, which would need its own NUL
# handling. The output is one path per line, so a path holding a
# newline prints as two lines: a residual bound of the line format, not of
# the read.
# `--phase` is accepted only as the second argument. KD-2: its base is the
# latest commit in `<run base>..HEAD` touching
# `plans/<job>/reports/phase-*-corrector.md` (the path, never the commit
# subject, KD-8); no `--diff-filter`, so a modified report counts, and `-1`
# takes the latest. With no such commit the base is the run base.

if [[ $# -lt 1 || $# -gt 2 || ( $# -eq 2 && $2 != --phase ) ]]; then
    echo "ERROR: usage: changed-files.sh <job> [--phase]"
    exit 2
fi
job=$1
# The job is one directory name under `plans/`. It lands in a git pathspec,
# where `*`, `?`, `[` and `\` are glob syntax: `j*` would match a sibling
# job's reports and yield a wrong base. `/`, `.` and `..` would leave
# `plans/`. `--phase` here is the flag with the job missing, which would
# otherwise read as a job with no item report: exit 1, `NO-BASE:`.
case "$job" in
    '' | . | .. | --phase | */* | *[*?[\\]*)
        printf 'ERROR: usage: changed-files.sh <job> [--phase]; not a job name: %s\n' "$job"
        exit 2
        ;;
esac

# Located as in `verify-step.sh`, whose comment explains the idiom. Here
# `BASH_SOURCE[0]` may be relative to the CWD, so the source precedes the
# `cd` below. An unset variable would trip `set -u`, whose exit 1 is
# `NO-BASE:`'s code.
case "${BASH_SOURCE[0]}" in
    */*) script_dir="${BASH_SOURCE[0]%/*}" ;;
    *) script_dir="." ;;
esac
# shellcheck source=SCRIPTDIR/exempt-paths.sh
if ! source "$script_dir/exempt-paths.sh" || [[ -z ${EXEMPT_PATHS_ALTERNATION:-} ]]; then
    echo "ERROR: cannot load EXEMPT_PATHS_ALTERNATION from exempt-paths.sh"
    exit 2
fi
exempt_re='^('"${EXEMPT_PATHS_ALTERNATION}"')$'

# The pathspecs are root-relative; from a subdirectory they would match
# nothing.
top=$(git rev-parse --show-toplevel) || {
    echo "ERROR: git rev-parse --show-toplevel failed"
    exit 2
}
cd "$top" || {
    echo "ERROR: cd to repository root failed"
    exit 2
}

first_commit=$(git log --no-show-signature --no-renames --diff-filter=A --reverse --format=%H -- "plans/$job/reports/item-*") || {
    echo "ERROR: git log failed"
    exit 2
}
first_commit=${first_commit%%$'\n'*}

if [[ -z $first_commit ]]; then
    printf 'NO-BASE: no committed plans/%s/reports/item-* report\n' "$job"
    exit 1
fi

# A root commit has no parent: an error, never a fallback base.
base_sha=$(git rev-parse --verify --quiet "${first_commit}^") || {
    printf 'ERROR: cannot resolve the parent of first item report commit "%s"\n' "$first_commit"
    exit 2
}

if [[ ${2:-} == --phase ]]; then
    phase_commit=$(git log -1 --format=%H --no-renames --no-show-signature "${base_sha}..HEAD" -- "plans/$job/reports/phase-*-corrector.md") || {
        echo "ERROR: git log for the phase boundary failed"
        exit 2
    }
    if [[ -n $phase_commit ]]; then
        base_sha=$phase_commit
    fi
fi

# A write failure would exit 1 under `set -e`, which reads as `NO-BASE:`.
printf 'BASE: %s\n' "$base_sha" || exit 2

exclude_prefix="plans/$job/"
# `--` keeps a path named `HEAD` from making the revision ambiguous.
git diff --name-only --no-renames -z "$base_sha" HEAD -- | while IFS= read -r -d '' path; do
    case "$path" in
        "$exclude_prefix"*) continue ;;
    esac
    if [[ $path =~ $exempt_re ]]; then
        continue
    fi
    printf '%s\n' "$path"
done || {
    echo "ERROR: git diff failed"
    exit 2
}

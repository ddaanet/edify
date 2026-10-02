#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# KD-1: the base is the parent of the earliest commit that added a
# `plans/<job>/reports/item-*` report. `--diff-filter=A --reverse` orders
# additions oldest first; the first line is that commit, and its parent is
# the base. `--no-show-signature` keeps a user's `log.showSignature` from
# printing verification lines ahead of the shas.
# KD-6: the changed-files list is the committed diff since that base
# (`<base> HEAD`, never the working tree), minus the job's own
# `plans/<job>/` record. Paths come from a NUL-delimited `git diff -z`, read
# with `read -r -d ''`, never split on whitespace or newlines. The output is
# one path per line, so a path holding a newline prints as two lines: a
# residual bound of the line format, not of the read.

if [[ $# -ne 1 ]]; then
    echo "ERROR: usage: changed-files.sh <job>"
    exit 2
fi
job=$1
# The job is one directory name under `plans/`. It lands in a git pathspec,
# where `*`, `?`, `[` and `\` are glob syntax: `j*` would match a sibling
# job's reports and yield a wrong base. `/`, `.` and `..` would leave
# `plans/`.
case "$job" in
    '' | . | .. | */* | *[*?[\\]*)
        printf 'ERROR: usage: changed-files.sh <job>; not a job name: %s\n' "$job"
        exit 2
        ;;
esac

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

first_commit=$(git log --no-show-signature --diff-filter=A --reverse --format=%H -- "plans/$job/reports/item-*") || {
    echo "ERROR: git log failed"
    exit 2
}
first_commit=${first_commit%%$'\n'*}

# A root commit has no parent: an error, never a fallback base.
base_sha=$(git rev-parse --verify --quiet "${first_commit}^") || {
    printf 'ERROR: cannot resolve the parent of first item report commit "%s"\n' "$first_commit"
    exit 2
}

printf 'BASE: %s\n' "$base_sha"

exclude_prefix="plans/$job/"
# `--` keeps a path named `HEAD` from making the revision ambiguous.
git diff --name-only -z "$base_sha" HEAD -- | while IFS= read -r -d '' path; do
    case "$path" in
        "$exclude_prefix"*) continue ;;
    esac
    printf '%s\n' "$path"
done || {
    echo "ERROR: git diff failed"
    exit 2
}

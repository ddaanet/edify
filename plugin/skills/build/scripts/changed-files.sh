#!/usr/bin/env bash
exec 2>&1
set -euo pipefail

# KD-1: the base is the parent of the earliest commit that added a
# `plans/<job>/reports/item-*` report. `--diff-filter=A --reverse` orders
# additions oldest first; the first line is that commit, and its parent is
# the base.
# KD-6: the changed-files list is the committed diff since that base
# (`<base> HEAD`, never the working tree), minus the job's own
# `plans/<job>/` record. Paths come from a NUL-delimited `git diff -z`, read
# with `read -r -d ''`, never split on whitespace or newlines.

if [[ $# -ne 1 ]]; then
    echo "ERROR: usage: changed-files.sh <job>"
    exit 2
fi
job=$1

first_commit=$(git log --diff-filter=A --reverse --format=%H -- "plans/$job/reports/item-*") || {
    echo "ERROR: git log failed"
    exit 2
}
first_commit=${first_commit%%$'\n'*}

base_sha=$(git rev-parse "${first_commit}^") || {
    echo "ERROR: git rev-parse failed"
    exit 2
}

printf 'BASE: %s\n' "$base_sha"

exclude_prefix="plans/$job/"
# Quoting "$exclude_prefix" in the case pattern disables globbing on it, so
# a job name holding a glob metacharacter still matches literally; only the
# trailing `*` is a wildcard.
git diff --name-only -z "$base_sha" HEAD | while IFS= read -r -d '' path; do
    case "$path" in
        "$exclude_prefix"*) continue ;;
    esac
    printf '%s\n' "$path"
done || {
    echo "ERROR: git diff failed"
    exit 2
}

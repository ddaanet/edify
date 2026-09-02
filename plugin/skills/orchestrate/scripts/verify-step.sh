#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

# Clean tree; ` M memory` is the submodule's resting state, not dirt.
# `git status` must succeed; only grep's exit 1 (every line filtered out) is
# a result rather than a failure, so tolerate that one code and nothing else.
porcelain=$(git status --porcelain)
if status=$(grep -vx ' M memory' <<<"$porcelain"); then
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

just precommit || {
    echo "PRECOMMIT: validation failed"
    exit 1
}

echo "CLEAN"
exit 0

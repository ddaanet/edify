#!/usr/bin/env bash
exec 2>&1
set -xeuo pipefail

if [[ $# -ne 1 ]]; then
    echo "ERROR: exactly one argument required: <test_file>"
    exit 1
fi

test_file="$1"

if [[ ! -f "$test_file" ]]; then
    echo "ERROR: test file not found: $test_file"
    exit 1
fi

# Run the test — non-zero exit means it failed (RED state).
# Default is pytest; a project with a different runner sets EDIFY_TEST_CMD to a
# command that takes the test file as its final argument, e.g.
#   EDIFY_TEST_CMD="go test -run" or EDIFY_TEST_CMD="npx vitest run"
read -r -a test_cmd <<< "${EDIFY_TEST_CMD:-pytest --no-header -q}"

if "${test_cmd[@]}" "$test_file"; then
    echo "RED REJECTED: test passed unexpectedly"
    exit 1
else
    echo "RED CONFIRMED"
    exit 0
fi

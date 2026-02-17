# Step D: SKILL.md Update Report

## File Modified

`agent-core/skills/worktree/SKILL.md`

## Changes

### 1. Added `--confirm` to rm invocation (line 92)

Mode C step 3 rm command changed from `claudeutils _worktree rm <slug>` to `claudeutils _worktree rm --confirm <slug>`. The skill is the intended invocation path and now passes `--confirm` as required by the updated CLI.

### 2. Updated exit code documentation (lines 96-98)

Previous exit code semantics (under "Handle `rm` exit codes"):
- Exit 1: Guard refused (unmerged commits) — escalate
- Exit 2: Unexpected error (branch deletion failed) — escalate

New exit code semantics:
- Exit 2: Safety gate refused (guard refused, dirty parent/submodule, or missing --confirm). Includes note that this shouldn't normally occur after successful merge because `--confirm` is passed and merge ensures merged state. Escalate with stderr.
- Exit 1: Operational error (branch deletion failed). Escalate with stderr.

Exit code order in documentation changed from 0/1/2 to 0/2/1 to match semantic grouping (safety gates before operational errors).

### 3. Added --force note to Usage Notes (line 138)

New bullet at end of Usage Notes section: documents `--force` flag as emergency escape hatch that bypasses all safety checks (confirm, dirty tree, guard).

## Verification

- Line 92 confirms rm invocation includes `--confirm`
- Lines 96-98 reflect new exit code semantics (2=safety gate, 1=operational error)
- Line 138 documents `--force` escape hatch
- No changes to Mode A, Mode B, pre-merge steps, or merge flow

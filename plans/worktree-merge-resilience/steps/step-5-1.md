# Step 5.1

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.1: Audit exit codes — reclassify conflict-pause exits to SystemExit(3)

**Objective:** Ensure every `raise SystemExit` in `merge.py` uses the correct code from D-1 semantics: exit 0 = success, exit 1 = error (recoverable, not a merge state issue), exit 2 = fatal (branch missing, merge state corrupt), exit 3 = conflicts need resolution (merge paused).

**Script Evaluation:** Prose — medium scope (read full merge.py, classify each exit, make targeted edits).

**Execution Model:** Sonnet (code audit + judgment on error vs conflict classification).

**Implementation:**
1. Read full `src/claudeutils/worktree/merge.py` (current state after Phases 1-4)
2. List every `raise SystemExit(N)` with line number and context
3. For each: classify as error (1), fatal (2), or conflict-pause (3) per D-1:
   - `SystemExit(3)`: any path where MERGE_HEAD is preserved and agent needs to resolve conflicts
   - `SystemExit(1)`: precommit failure, git command error, unrecognized merge failure (non-conflict)
   - `SystemExit(2)`: branch not found, merge state corrupt (`slug not fully merged`, `nothing to commit and branch not merged`)
4. Update any misclassified exits (Phases 1-4 may have used `SystemExit(1)` for conflict-pause paths)

**Expected Outcome:** All conflict-pause exits use `SystemExit(3)`. No exit 1 on paths where MERGE_HEAD is preserved. No exit 3 on precommit failure or git error paths.

**Error Conditions:**
- If a path is ambiguous (could be error or conflict-pause): classify as exit 1 and add inline comment explaining the distinction
- If audit finds unexpected paths: STOP and report

**Validation:**
- `grep -n "SystemExit" src/claudeutils/worktree/merge.py` — manually verify each entry
- `just precommit` passes

---

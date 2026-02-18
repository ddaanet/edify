# Cycle 1.3

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.3: `merge()` routes `parent_conflicts` state to exit 3

**RED Phase:**

**Test:** `test_merge_reports_and_exits_3_when_parent_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- Exit code is 3 when `merge(slug)` called with MERGE_HEAD present and unresolved conflicts
- MERGE_HEAD still exists after the call (no `--abort` was run)
- Output contains name of conflicted file
- No traceback in output

**Expected failure:** `SystemExit(1)` — current Phase 1 clean-tree check rejects the dirty tree before reaching any conflict detection

**Why it fails:** Current code validates clean tree before checking merge state; staged conflict-marker files fail the clean check.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`

**Test setup:**
1. Create repo, branch with different content in `src/feature.py`, main with different content in same file
2. Start merge: `subprocess.run(["git", "merge", "--no-commit", "--no-ff", slug], ...)`
3. Verify MERGE_HEAD exists and `git diff --name-only --diff-filter=U` is non-empty
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit_code == 3, MERGE_HEAD still present (subprocess check), conflicted filename in output.

**GREEN Phase:**

**Implementation:** The routing from Cycle 1.2 already dispatches `parent_conflicts` to stub. Implement stub to list conflicts from `git diff --name-only --diff-filter=U` and exit 3.

**Behavior:**
- For `parent_conflicts` route: get conflict list via `git diff --name-only --diff-filter=U`
- Print each conflicted file
- `raise SystemExit(3)` — no `--abort`, no `clean -fd` (D-3, D-7)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Replace stub in `parent_conflicts` branch of `merge()` with conflict listing + exit 3
  Location hint: `parent_conflicts` case in `merge()` dispatch

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`
**Verify MERGE_HEAD preserved:** subprocess check in test; verify MERGE_HEAD still valid after CliRunner call.
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

**CHECKPOINT after Cycle 1.3:** Verify all in-progress states route correctly:
- `merged` + `parent_resolved` → Phase 4
- `parent_conflicts` → exit 3, MERGE_HEAD preserved
- Run: `pytest tests/test_worktree_merge_merge_head.py -v`

---

# Cycle 3.2

**Plan**: `plans/worktree-merge-resilience/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Cycle 3.2: Untracked file collision handling — `git add` + retry (FR-3, D-4)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:137-160` — understand how Phase 3 detects the merge-abort (no MERGE_HEAD) vs merge-conflict (MERGE_HEAD present) distinction. The untracked file case produces no MERGE_HEAD (git refused before starting the merge).

**RED Phase:**

**Tests:** Update `test_merge_aborts_cleanly_when_untracked_file_blocks` + new test `test_merge_untracked_file_conflict_markers`.

Both in `tests/test_worktree_merge_errors.py`.

**Test A — updated `test_merge_aborts_cleanly_when_untracked_file_blocks`:**
The existing test setup already has different content on main ("# Untracked\n") vs branch ("# Branch\n"). No setup change needed. After `git add` + retry, the merge produces conflict markers (exit 3). Update assertions only — the test becomes a conflict-path test rather than an error test.

Updated assertions for `test_merge_aborts_cleanly_when_untracked_file_blocks`:
- `result.exit_code == 3` (was `!= 0`)
- MERGE_HEAD exists after call (merge started after git add + retry)
- Conflict markers (`<<<<<<<`) present in the untracked file (file now tracked and conflicted)
- `"Traceback"` not in output

**Test B — new `test_merge_untracked_file_same_content_auto_resolved`:**
This is a success-path test: same-content auto-merge → Phase 4 runs → `just precommit` is called. Use `mock_precommit` fixture.

Assertions:
- When untracked file on main has SAME content as branch, `merge(slug)` exits 0
- File is tracked after merge (no longer untracked)
- `"Traceback"` not in output

**Expected failure (both tests):**
- Test A: currently `exit_code != 0` check passes, but after update to `exit_code == 3` + MERGE_HEAD check: current code exits with "Merge failed: error: Untracked working tree file..." (exit 1), no MERGE_HEAD, no conflict markers → test fails
- Test B: currently no test; new test fails because current code exits 1 on untracked file (doesn't attempt git add + retry)

**Why it fails:** `_phase3_merge_parent` detects no-MERGE_HEAD case as fatal error (exit 1) without attempting recovery.

**Verify RED:**
- `pytest tests/test_worktree_merge_errors.py::test_merge_aborts_cleanly_when_untracked_file_blocks -v`
- `pytest tests/test_worktree_merge_errors.py::test_merge_untracked_file_same_content_auto_resolved -v`

**GREEN Phase:**

**Implementation:** Add untracked-file collision detection and `git add` + retry logic to `_phase3_merge_parent`.

**Behavior:**
- When `git merge --no-commit --no-ff slug` fails (non-zero return) AND MERGE_HEAD is absent (merge refused before starting):
  - Inspect `result.stderr` for untracked-file markers: `"error: Untracked working tree file"` or `"Your local changes to the following files would be overwritten by merge"`
  - Parse file paths from the error output (files listed one per line after the marker, before the next blank line)
  - For each file: `git add <file>` (converts untracked to tracked, letting git perform three-way merge on retry)
  - Retry: `git merge --no-commit --no-ff slug` a second time
  - The retry result is handled by the normal conflict pipeline:
    - If retry exit 0: continue (auto-resolved or clean merge)
    - If retry exit non-zero + MERGE_HEAD: proceed to conflict reporting (exit 3)
  - If no untracked-file markers in stderr: this is an unrecognized error → `click.echo(f"Merge failed: {stderr}")` + `raise SystemExit(1)` (preserves existing behavior for other error types)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: In `_phase3_merge_parent`, in the no-MERGE_HEAD branch (currently `click.echo(f"Merge failed: {stderr}")` + `raise SystemExit(1)` at lines 155-157): add untracked detection + git add + retry before falling through to existing error path
  Location hint: `_phase3_merge_parent`, between lines 154 and 157 (after the no-MERGE_HEAD check)

**Verify GREEN:**
- `pytest tests/test_worktree_merge_errors.py -v`
- `pytest tests/ -k "merge" -v` (full regression check)

---

**Phase 3 STOP conditions:**
- MERGE_HEAD absent after Cycle 3.1 GREEN → STOP, --abort still being called (verify with grep)
- Untracked file `git add` fails (file doesn't exist) → STOP, path parsing from stderr incorrect
- Cycle 3.2 retry never triggers → STOP, untracked detection pattern not matching git's actual error message (verify with real git output)
- Regression in auto-resolution tests (session.md, learnings.md) → STOP, changed code broke existing conflict handling path
- NFR-2 grep fails → STOP before proceeding to Phase 4

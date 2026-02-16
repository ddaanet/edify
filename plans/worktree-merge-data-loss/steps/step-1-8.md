# Cycle 1.8

**Plan**: `plans/worktree-merge-data-loss/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Cycle 1.8: No `git branch -D` in output — verify no destructive suggestions in stderr/stdout

**Type:** Transformation (Regression guard)

**Note:** This is a regression guard for FR-5 (design.md line 24). Current code emits `"use: git branch -D {slug}"` in the branch delete fallback. After Cycles 1.4-1.7 restructure rm(), this old fallback code is obsolete — the guard handles all branch deletion paths with appropriate flags. This cycle removes the obsolete code and tests that no destructive suggestions remain.

**RED Phase:**

**Test:** `test_rm_no_destructive_suggestions` in `tests/test_worktree_rm_guard.py`

**Assertions:**
- Test three scenarios: merged branch removal, focused-session removal, guard refusal
- For each scenario: capture stdout and stderr
- Assert `"git branch -D"` NOT in stdout
- Assert `"git branch -D"` NOT in stderr
- Run against CURRENT code to verify RED failure

**Expected failure:** Output contains `"git branch -D"` string from old branch delete fallback code (cli.py:373). The focused-session scenario is most likely to trigger it: the branch is unmerged, so the old `git branch -d` at line 369 fails, and line 373 emits the destructive suggestion. If Cycles 1.5-1.6 already replaced this code path, RED may pass for all scenarios — in that case, the GREEN phase is a no-op cleanup verification and the test remains as a regression guard.

**Why it fails:** Old branch delete fallback code still present — emits destructive suggestion when `-d` fails for unmerged branches

**Verify RED:** `pytest tests/test_worktree_rm_guard.py::test_rm_no_destructive_suggestions -v`

**GREEN Phase:**

**Implementation:** Remove destructive suggestion from rm() output

**Behavior:**
- Remove the old branch delete fallback block (`subprocess.run(["git", "branch", "-d", slug])` + error message suggesting `-D`)
- Guard (Cycles 1.4-1.6) now handles all branch deletion scenarios with appropriate flags (`-d` for merged, `-D` for focused-session-only)
- No CLI output should suggest manual git commands

**Approach:** Delete obsolete branch deletion code — guard replacement makes it redundant

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Remove old branch delete fallback block (the `subprocess.run` with `-d` and its error message)
  Location hint: Branch deletion section (may have shifted from original line 369 due to Cycles 1.4-1.7 edits)

**Verify GREEN:** `pytest tests/test_worktree_rm_guard.py::test_rm_no_destructive_suggestions -v`
**Verify no regression:** `pytest tests/test_worktree_rm_guard.py -v` (full Track 1 suite)

---
